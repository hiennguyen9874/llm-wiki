---
type: Concept
title: SGLang HiCache Runtime Storage Attach/Detach
description: Dynamically attach or detach HiCache L3 storage backends at runtime via HTTP API with idle-state safety checks.
tags: [sglang, hicache, kv-cache, storage-backend]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:59:44Z }
sources:
  - id: sgl-hicache-attach
    resource: ../raw/sglang/advanced_features/hicache_storage_runtime_attach_detach.mdx
    title: Runtime Attach/Detach HiCache Storage Backend (No Restart)
---

SGLang can dynamically attach or detach the HiCache L3 storage backend (e.g. `mooncake` / `hf3fs` / `nixl` / `file` / `aibrix` / `eic`) while already running and serving traffic, with no process restart, gated by a strict scheduler-idle check[^sgl-hicache-attach].

## Control path

Runtime storage operations flow through[^sgl-hicache-attach]:

1. **HTTP server** (`python/sglang/srt/entrypoints/http_server.py`) — exposes `PUT /hicache/storage-backend`, `DELETE /hicache/storage-backend`, `GET /hicache/storage-backend`.
2. **TokenizerManager** (`python/sglang/srt/managers/tokenizer_communicator_mixin.py`) — forwards the request to the scheduler via `_Communicator`.
3. **Scheduler** (`python/sglang/srt/managers/scheduler.py`) — performs the strict idle check, then calls `tree_cache.attach_storage_backend(...)` / `detach_storage_backend(...)`.
4. **HiRadixCache** (`python/sglang/srt/mem_cache/hiradix_cache.py`) — parses `hicache_storage_backend_extra_config_json` (backend config plus prefetch knobs), then calls `cache_controller.attach_storage_backend(...)` / `detach_storage_backend(...)`.
5. **HiCacheController** (`python/sglang/srt/managers/cache_controller.py`) — creates/destroys the backend instance via `StorageBackendFactory` and starts/stops backend background threads (prefetch/backup) at runtime.

## Idle-state requirement

Attach/detach is allowed only when the service is idle. The scheduler checks `_is_idle_for_hicache_storage_op()`[^sgl-hicache-attach]:

- `_is_no_request()` is true (covers running/overlap/pp/disagg and other active states).
- `waiting_queue` is empty.
- `grammar_queue` is empty (if the grammar backend is enabled).

If the condition is not met, the API fails fast with HTTP 400 and does not modify service state, e.g. `Reject attach: scheduler is not idle. #queue-req=... #running-req=...`[^sgl-hicache-attach].

Operationally, drain upstream traffic and wait for the server to become idle before calling attach/detach[^sgl-hicache-attach].

## Data-parallel semantics

When `dp_size > 1`, the tokenizer dispatches the request to all DP scheduler instances and aggregates responses[^sgl-hicache-attach]:

- Final `success` is true only if all DP ranks succeed.
- Final `message` concatenates messages from all DP ranks.

This avoids silent partial success, but overall failure can occur after some ranks already succeeded. There is currently no automatic partial rollback across DP ranks (noted as TODO in code)[^sgl-hicache-attach].

Operational guidance: keep backend config identical across ranks; if attach fails, immediately call detach (best-effort/idempotent), fix the config, then retry attach[^sgl-hicache-attach].

## HTTP admin API

Assuming the server is at `http://127.0.0.1:30000`[^sgl-hicache-attach]:

Query current backend status:

```bash
curl -s http://127.0.0.1:30000/hicache/storage-backend
```

Example response:

```json
{
  "hicache_storage_backend": "mooncake",
  "hicache_storage_backend_extra_config": "{\"master_server_address\":\"127.0.0.1:50051\", ...}"
}
```

Attach (enable) a backend:

```bash
curl -s -X PUT http://127.0.0.1:30000/hicache/storage-backend \
  -H 'Content-Type: application/json' \
  -d '{
    "hicache_storage_backend": "mooncake"
  }'
```

Attach with backend plus prefetch configuration:

```bash
curl -s -X PUT http://127.0.0.1:30000/hicache/storage-backend \
  -H 'Content-Type: application/json' \
  -d '{
    "hicache_storage_backend": "mooncake",
    "hicache_storage_backend_extra_config_json": "{\"master_server_address\":\"127.0.0.1:50051\",\"protocol\":\"tcp\",\"global_segment_size\":\"4gb\",\"prefetch_threshold\":256}",
    "hicache_storage_prefetch_policy": "timeout"
  }'
```

`hicache_storage_backend_extra_config_json` can carry both backend configuration (e.g. Mooncake master/metadata/protocol) and prefetch knobs (`prefetch_threshold`, `prefetch_timeout_base`, `prefetch_timeout_per_ki_token`, `hicache_storage_pass_prefix_keys`)[^sgl-hicache-attach].

Detach (disable) the backend:

```bash
curl -s -X DELETE http://127.0.0.1:30000/hicache/storage-backend
```

Detach stops SGLang from using the L3 backend and stops prefetch/backup threads; it does not delete data already stored in Mooncake/HF3FS or other remote backends[^sgl-hicache-attach].

## Behavior and caveats

- No restart required: attach/detach switches in-process at runtime[^sgl-hicache-attach].
- Must be idle, otherwise the request is rejected to avoid consistency issues[^sgl-hicache-attach].
- Host KV layout constraints still apply: e.g. Mooncake still requires layouts like `page_first` / `page_first_direct` / `page_head`; attach fails if the server HiCache host-memory layout does not satisfy the backend requirements[^sgl-hicache-attach].
- Observability: after attach, `server_args.hicache_storage_backend*` is updated on both tokenizer and scheduler sides; if metrics are enabled, attach creates a storage metrics collector in `HiRadixCache` on demand[^sgl-hicache-attach].

## Relationships

- Uses [SGLang HiCache System Design](sglang-hicache-design.md) for the L1/L2/L3 hierarchy, HiRadixCache, and storage-controller mechanics.
- Uses [SGLang HiCache Best Practices](sglang-hicache-best-practices.md) for memory-layout choice, prefetch policies, and Mooncake/HF3FS deployment context.

[^sgl-hicache-attach]: Runtime Attach/Detach HiCache Storage Backend (No Restart) — `../raw/sglang/advanced_features/hicache_storage_runtime_attach_detach.mdx`.
