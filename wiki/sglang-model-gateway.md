---
type: Concept
title: SGLang Model Gateway
description: High-performance model-routing gateway for SGLang with multi-protocol routing, PD disaggregation, load balancing, reliability, and enterprise controls.
tags: [sglang, gateway, routing, load-balancing, observability]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T16:00:00Z }
sources:
  - id: sgl-gateway
    resource: ../raw/sglang/advanced_features/sgl_model_gateway.mdx
    title: SGLang Model Gateway
---

SGLang Model Gateway (former Router) is a Rust-based routing tier that centralizes worker lifecycle, balances HTTP/gRPC/OpenAI-compatible traffic, and keeps conversation history, MCP tooling, and agentic `/v1/responses` loops inside the router boundary for privacy-sensitive deployments[^sgl-gateway].

## Architecture

- **Control plane:** Worker Manager discovers capabilities via `/get_server_info` and `/get_model_info`, tracks load, and maintains the registry; Job Queue serializes add/remove with per-worker status at `/workers/{worker_id}`; Load Monitor feeds cache-aware and power-of-two policies; Health Checker updates readiness, circuit-breaker state, and metrics; Tokenizer Registry loads tokenizers asynchronously from HuggingFace or local paths[^sgl-gateway].
- **Data plane:** HTTP regular and PD routers serve `/generate`, chat/completions, embeddings, rerank, classify, tokenize, conversations, responses, and admin endpoints; gRPC router streams tokenized requests to SRT gRPC workers with in-process Rust tokenizer, reasoning parser, and tool parser in single-stage or PD topologies; OpenAI router proxies external OpenAI-compatible vendors while keeping history and multi-turn orchestration local[^sgl-gateway].
- **Storage and privacy:** Router-tier history backends reuse the same context across models and MCP loops without sending stored context upstream[^sgl-gateway].

## Deployment modes

- **Co-launch:** `python -m sglang_router.launch_server` starts router plus SGLang workers in one process; router-specific flags use the `--router-` prefix in this mode[^sgl-gateway].
- **Separate HTTP:** workers run `python -m sglang.launch_server` independently; router points at `--worker-urls http://...` with `--policy cache_aware`[^sgl-gateway].
- **gRPC:** workers start with `--grpc-mode`; router uses `grpc://` worker URLs plus `--model-path` or `--tokenizer-path` for in-gateway tokenization, reasoning, and tool parsing[^sgl-gateway].
- **PD disaggregation:** `--pd-disaggregation` with `--prefill <url> [bootstrap-port]` and `--decode <url>`, plus optional `--prefill-policy` and `--decode-policy`; prefill metadata merges with decode output for streaming[^sgl-gateway].
- **OpenAI proxy:** `--backend openai` with exactly one `--worker-urls` entry and `--history-backend memory` keeps history and MCP sessions local[^sgl-gateway].
- **Inference Gateway (`--enable-igw`):** one gateway dynamically instantiates multiple HTTP regular/PD and gRPC router stacks with per-model policies; workers register dynamically via `POST /workers` with `model_id`, `priority`, and `labels`[^sgl-gateway].

## API surface

- **Inference:** `POST /generate`, `POST /v1/chat/completions`, `POST /v1/completions`, `POST /v1/embeddings`, `POST /v1/rerank` and `/rerank`, `POST /v1/classify`[^sgl-gateway].
- **Tokenization:** `POST /v1/tokenize` and `/v1/detokenize` with single or batch prompts; tokenizer registry via `POST /v1/tokenizers` returning async `pending` job status, `GET /v1/tokenizers`, `GET /v1/tokenizers/{id}`, `GET /v1/tokenizers/{id}/status`, and `DELETE /v1/tokenizers/{id}`[^sgl-gateway].
- **Parsing:** `POST /parse/reasoning` separates `<think>` reasoning from normal text; `POST /parse/function_call` parses tool calls[^sgl-gateway].
- **Classification:** `POST /v1/classify` returns `label`, `probs`, and `num_classes`; labels come from HuggingFace `id2label` with `LABEL_N` fallback; implementation reuses the embedding backend with softmax over logits; supported on HTTP and gRPC routers[^sgl-gateway].
- **Conversations and responses:** `POST/GET/cancel/DELETE /v1/responses/{id}` plus `/v1/responses/{id}/input_items`; conversation CRUD at `/v1/conversations` and `/v1/conversations/{id}` with item list/add/get/delete under `/items`[^sgl-gateway].
- **Workers:** `POST /workers` queues registration with `202 Accepted`; `GET /workers` lists health, load, and policy metadata; `GET/PUT/DELETE /workers/{worker_id}` inspects or queues update/removal; entries expose `id`, `url`, `model_id`, `priority`, `cost`, `worker_type`, `is_healthy`, `load`, and `connection_mode`[^sgl-gateway].
- **Admin and health:** `GET /liveness`, `/readiness`, `/health`, `/health_generate`, `/engine_metrics`, `/v1/models`, `/get_model_info`, `/get_server_info`, `GET /get_loads`, `POST /flush_cache`, and WASM module APIs `POST/GET /wasm` and `DELETE /wasm/{module_uuid}`[^sgl-gateway].

## Load balancing

Policies are `random`, `round_robin`, `power_of_two`, `cache_aware` (default), and `bucket` with dynamic load boundaries[^sgl-gateway].

Cache-aware defaults are `--cache-threshold 0.3`, `--balance-abs-threshold 64`, `--balance-rel-threshold 1.5`, `--eviction-interval-secs 120`, and `--max-tree-size 67108864`; source examples show tighter tuning such as `0.5` and `32`, which are tuning illustrations rather than changed defaults[^sgl-gateway].

## Reliability and flow control

- **Retries:** exponential backoff with defaults `--retry-max-retries 5`, `--retry-initial-backoff-ms 50`, `--retry-max-backoff-ms 5000`, `--retry-backoff-multiplier 2.0`, `--retry-jitter-factor 0.1`, and `--disable-retries false`; source examples use larger backoff and different multiplier/jitter as tuning illustrations; retryable codes are `408`, `429`, `500`, `502`, `503`, `504`[^sgl-gateway].
- **Circuit breaker:** per-worker breaker with defaults `--cb-failure-threshold 5`, `--cb-success-threshold 2`, `--cb-timeout-duration-secs 30`, `--cb-window-duration-secs 60`; states are Closed, Open, and Half-Open[^sgl-gateway].
- **Rate limiting and queuing:** `--max-concurrent-requests`, `--rate-limit-tokens-per-second`, `--queue-size`, and `--queue-timeout-secs`; overflow waits in FIFO and returns `429` when full or `408` on queue timeout[^sgl-gateway].
- **Health checks:** `--health-check-interval-secs 30`, `--health-check-timeout-secs 10`, `--health-success-threshold 2`, `--health-failure-threshold 3`, `--health-check-endpoint /health`[^sgl-gateway].

## Reasoning, tool calls, and tokenizers

- **Reasoning parsers:** `deepseek-r1`, `qwen3`, `qwen3-thinking`, `kimi`, `glm45` for GLM-4.5/4.6/4.7, `step3`, and `minimax`; all use `<think>`-style delimiters except Kimi which uses Unicode think tokens; gRPC mode applies incremental streaming parsing with buffer and partial-token handling[^sgl-gateway].
- **Tool-call parsers:** table lists `json`, `python`, and `xml`; one co-launch example uses a `llama` parser value not present in that table, so treat `llama` as observed but undocumented in this source[^sgl-gateway].
- **Tokenizer sources:** HuggingFace model ID, local `tokenizer.json` or directory, and auto-detected Tiktoken for OpenAI GPT models; flags are `--model-path`, `--tokenizer-path`, and `--chat-template`[^sgl-gateway].
- **Tokenizer cache:** L0 exact-match whole-string cache and L1 prefix-match cache, with `--enable-l0-cache`, `--l0-max-entries`, `--enable-l1-cache`, and `--l1-max-memory`[^sgl-gateway].

## MCP, discovery, and history

- **MCP client:** native client configured with `--mcp-config-path`; transport table lists STDIO, SSE, and Streamable, while the overview also names HTTP, so HTTP support is unclear from this source alone; YAML covers `servers`, `pool`, `proxy`, and `inventory` with tool TTL and refresh intervals; credential fields are present in the example but omitted here[^sgl-gateway].
- **Kubernetes discovery:** `--service-discovery` with `--selector`, `--service-discovery-namespace`, and `--service-discovery-port`; PD mode uses `--prefill-selector` and `--decode-selector`; prefill bootstrap ports travel via the `sglang.ai/bootstrap-port` annotation; RBAC needs `get`, `list`, and `watch` on pods[^sgl-gateway].
- **History backends:** `memory` default, `none`, `oracle`, `postgres`, and `redis` via `--history-backend`; Oracle uses ATP connection, wallet, user, password, and pool variables; PostgreSQL uses a database URL variable; Redis uses URL, pool, and retention variables with `--redis-retention-days 30` default and `-1` for persistent storage; all secret values are redacted here[^sgl-gateway].

## Extensibility and bindings

- **WASM middleware:** sandboxed modules with memory isolation and no network or filesystem access; attach points are `OnRequest` before forwarding and `OnResponse` after worker reply; actions are `Continue`, `Reject(status)`, and `Modify(...)`; bundled examples cover auth, per-client rate limiting, and logging; interface lives at `src/wasm/interface`; build targets `wasm32-wasip2` as a `wasm-tools` component; deploy with `--enable-wasm` and `/wasm` APIs; defaults cap memory at 1024 pages, execution at 1000 ms, stack at 1 MB, and module cache at 10 per worker[^sgl-gateway].
- **WASM limit:** rate-limit state is per-worker thread and not shared across gateway replicas, so production global limiting needs a shared layer such as Redis[^sgl-gateway].
- **Python bindings:** PyO3 wrapper used as gateway launcher with `RouterArgs`, `Router.from_args()`, and CLIs `smg launch`, `smg server`, and `python -m sglang_router.launch_router`; install via `sglang-router` or `maturin` build[^sgl-gateway].
- **Go bindings:** gRPC client library with Rust FFI tokenization described as thread-safe and lock-free, streaming with context cancellation, configurable channel buffers, and built-in tool-call parsing and chat templates; examples cover simple, streaming, and OpenAI-compatible server shapes; requires Go 1.24+ and Rust[^sgl-gateway].
- **Binding choice:** Python launches and manages the gateway including discovery and PD mode; Go builds client applications, Go microservice integrations, and custom OpenAI-compatible proxies[^sgl-gateway].

## Security

Modes are no authentication by default, router-only, worker-only, and full router-plus-worker authentication; clients use `Authorization: Bearer` against the router and workers can carry per-worker API keys[^sgl-gateway].

- **Gateway TLS:** `--tls-cert-path` plus `--tls-key-path` enables HTTPS via rustls with ring; both are required, otherwise the gateway falls back to HTTP[^sgl-gateway].
- **Worker mTLS:** `--client-cert-path` plus `--client-key-path` with repeatable `--ca-cert-path` secures HTTP worker traffic; implementation uses one shared HTTP client and TCP keepalive, assuming a single security domain[^sgl-gateway].

## Observability

Prometheus exposes `40+` metrics, by default on `0.0.0.0:29000` via `--prometheus-host` and `--prometheus-port`[^sgl-gateway].

- **Families:** `smg_http_*`, `smg_router_*` including TTFT, TPOT, tokens, and generation duration, `smg_worker_*` including pool, connections, health, selection, errors, retries, `smg_worker_cb_*` for breaker state and transitions, plus `smg_discovery_*`, `smg_mcp_*`, and `smg_db_*`[^sgl-gateway].
- **Duration buckets:** from 1 ms through 120 s, 180 s, and 240 s[^sgl-gateway].
- **Tracing:** `--enable-trace` with OTLP/gRPC export, W3C propagation for HTTP and gRPC, batch processing, and service name `sgl-router`[^sgl-gateway].
- **Logging and IDs:** structured logs with `--log-level debug|info|warn|error` and optional `--log-dir`; configurable `--request-id-headers` propagate correlation IDs and responses carry `x-request-id`[^sgl-gateway].

## Production guidance

- **High availability:** replicas do not share worker registry, radix cache tree, breaker state, or rate limits; each replica discovers workers independently; cache-hit reduction of `10-20%` is expected and optional load-balancer session affinity can recover locality; horizontal replicas are preferred over one large instance[^sgl-gateway].
- **Performance:** gRPC mode is recommended for SGLang throughput because tokenization, reasoning parsing, tool parsing, streaming, and reduced serialization stay in Rust; tuning guidance favors `cache_aware`, concurrency at `2-4x` worker count, queue at `2x` concurrency, and request timeouts sized to maximum generation length; the source claims roughly `30%` latency reduction for repeated prompts with cache-aware routing[^sgl-gateway].
- **Kubernetes:** label regular workers and separate prefill/decode labels with bootstrap-port annotations; gateway discovery flags mirror those labels; Prometheus scrapes `:29000/metrics` with PromQL dashboards for request rate/latency, worker health, breaker state, gRPC TTFT/TPOT and token throughput, queueing/retries, and MCP execution, plus alerts for high error rate, open breakers, high P99 latency, and zero healthy workers[^sgl-gateway].

## Configuration defaults

- **Core:** `--host 127.0.0.1`, `--port 30000`, `--worker-urls []`, `--policy cache_aware`, `--max-concurrent-requests -1` meaning disabled, `--request-timeout-secs 600`, `--max-payload-size 256MB`[^sgl-gateway].
- **PD:** `--pd-disaggregation false`, `--prefill []`, `--decode []`, `--prefill-policy` and `--decode-policy` unset by default, `--worker-startup-timeout-secs 600`[^sgl-gateway].
- **Discovery:** `--service-discovery` opt-in; worker port default is `80` in the reference table while examples use `8000`, so set the port explicitly[^sgl-gateway].

## Troubleshooting

- Workers never ready: raise `--worker-startup-timeout-secs` and verify health probes before router startup[^sgl-gateway].
- Hot workers: inspect per-worker request metrics and tune `--balance-*` and `--cache-threshold`[^sgl-gateway].
- Breaker flapping: raise failure threshold, lengthen timeout or window, or temporarily disable retries[^sgl-gateway].
- Queue `429`: raise `--queue-size`, lower client concurrency, or align `--max-concurrent-requests` with downstream capacity[^sgl-gateway].
- Memory growth: lower `--max-tree-size` or shorten `--eviction-interval-secs`[^sgl-gateway].
- gRPC failures: confirm workers use `--grpc-mode` and the router has `--model-path` or `--tokenizer-path`[^sgl-gateway].
- Private-model tokenizer failures: check HuggingFace credentials and local path access; credential values omitted[^sgl-gateway].

## Relationships

- Uses [SGLang PD Disaggregation](sglang-pd-disaggregation.md) — gateway PD flags and router topology for separated prefill/decode serving.
- Uses [SGLang Reasoning Parser](sglang-reasoning-parser.md) — gateway-side `--reasoning-parser` and `/parse/reasoning` complement server-side reasoning separation.
- Uses [SGLang Observability](sglang-observability.md) — server observability counterpart to gateway `smg_*` metrics, tracing, and request-ID logging.
- Uses [SGLang Server Arguments](sglang-server-arguments.md) — worker launch surface fronted by gateway deployment modes.
- Uses [SGLang Hyperparameter Tuning](sglang-hyperparameter-tuning.md) — gateway-based data-parallel alternative to server `--dp-size` tuning.

## Coverage limits

- Referenced `examples/wasm/`, `bindings/golang/examples/`, and `src/wasm/interface` were not inspected; WASM and Go example detail beyond the names and shapes above is outside verified scope[^sgl-gateway].
- Example credentials, tokens, database URLs, and API keys were redacted; only flag and variable names are preserved[^sgl-gateway].
- Throughput and latency figures are source claims without supporting measurements in this source[^sgl-gateway].

[^sgl-gateway]: SGLang Model Gateway — `../raw/sglang/advanced_features/sgl_model_gateway.mdx`, covering control/data/storage architecture, co-launch / separate HTTP / gRPC / PD / OpenAI-proxy / IGW deployment, inference / tokenize / parse / classify / conversations / responses / workers / admin APIs, cache-aware and other balancing policies, retries / circuit breaker / rate-limit / health checks, reasoning / tool / tokenizer handling, MCP / Kubernetes discovery / history backends, WASM middleware, Python and Go bindings, TLS / mTLS / API-key security, Prometheus / OTel / logging observability, HA / performance / Kubernetes / PromQL production guidance, configuration defaults, and troubleshooting.
