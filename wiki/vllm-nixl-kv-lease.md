---
type: Concept
title: vLLM NIXL KV Cache Lease Renewal
description: Heartbeat-renewed short leases letting prefill reclaim KV blocks quickly on decode failure while keeping them alive under decode overload.
tags: [vllm, kv-cache, disaggregated-prefill, nixl, lease, heartbeat]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: nixl-lease
    resource: ../raw/vllm/design/nixl_kv_cache_lease.md
    title: NIXL KV Cache Lease Renewal
---

vLLM disaggregated prefill/decode pins completed-prefill KV blocks on the prefill instance (P) under a short initial lease (default 30s); the decode instance (D) renews the lease with periodic heartbeats while the request is queued or in-flight, so P reclaims blocks within seconds if D dies but holds them indefinitely while D is healthy yet overloaded[^nixl-lease].

## Problem

- **Single-timeout retention:** the original design held P blocks until a single large timeout (`VLLM_NIXL_ABORT_REQUEST_TIMEOUT`, default 480s); a crashed or disconnected D left gigabytes of dead blocks pinned for up to 8 minutes, starving later prefill requests[^nixl-lease].
- **Overload risk of short timeouts:** simply lowering that timeout frees blocks before an overloaded D schedules the queued request, wasting completed prefill work and forcing recomputation[^nixl-lease].

## Lease lifecycle

When P finishes prefill it pins KV blocks with `kv_lease_duration` (default 30s). Blocks are then held until[^nixl-lease]:

1. **Transfer completes** — P receives a read-completion notification and frees blocks immediately.
2. **Heartbeat arrives** — each heartbeat extends expiry by `lease_duration * 2/3` (~20s at defaults), renewable indefinitely.
3. **Lease expires** — with no heartbeat, P reclaims blocks on expiry.

## Transport

Heartbeats reuse NIXL's existing notification system (`send_notif` / `get_new_notifs`) instead of a new channel; the medium is backend-specific with automatic IB/RoCE-to-TCP fallback. One batched heartbeat per iteration from D to a given P renews all requests D has pinned on that P[^nixl-lease].

## Decode-side tracking

Heartbeating must start when a request enters D's scheduler, not when it executes, because waiting-queue delay is unbounded under load[^nixl-lease]:

- `NixlConnectorScheduler.on_new_request()` starts tracking requests with `do_remote_prefill=True`, grouped by `remote_engine_id` for batching.
- Each scheduler step packages heartbeat metadata into `NixlConnectorMetadata`, throttled to `lease_duration // 6` (~5s at defaults).
- Tracking stops on KV-transfer completion (`update_connector_output`) or request finish/abort (`request_finished`).

## Worker behavior

- **D sending:** `start_load_kv()` (every forward pass) reads `metadata.heartbeat_by_engine` and sends batched `HB:` notifications. If D has not yet handshaked with that P — common for still-queued requests — it triggers a proactive handshake in a background thread, defers the heartbeat one step, and thereby also speeds up the eventual RDMA read[^nixl-lease].
- **P receiving:** `_get_new_notifs()` routes messages starting with `"HB:"` to `_handle_heartbeat()`, which applies `max(old_expiry, now + extension)` so leases are never accidentally shortened[^nixl-lease].
- **Timing:** sending and processing run in the forward loop, not a background thread; heartbeat interval (~5s) and extension (~20s) are an order of magnitude larger than a typical forward pass, avoiding lock complexity[^nixl-lease].

## Bidirectional transfer exception

For multi-turn conversations where D caches KV blocks that P later pulls, the next-turn timing is client-controlled, so heartbeats do not apply. A separate fixed `decoder_kv_blocks_ttl` (default 480s) bounds D-side retention; D reports the expiry and P corrects for the unrelated `perf_counter` clocks using a handshake round-trip clock-offset estimate before comparing[^nixl-lease].

## Key design decisions

- **Per-request leasing:** P has no notion of its D until the router assigns one after prefill, so leases attach to requests; D batches extensions by `remote_engine_id` toward the same P[^nixl-lease].
- **No extra transport:** NIXL notifications already handle backend selection and fallback across NIXL-supported transports[^nixl-lease].
- **Proactive handshake:** early connection for queued requests needing heartbeats also accelerates the later KV transfer[^nixl-lease].
- **Heterogeneous tensor parallelism:** when P TP > D TP (e.g., 4 vs 2), one D worker pulls from multiple P workers and must heartbeat all of them; when D TP > P TP, one P receives redundant refreshes with no downside[^nixl-lease].

## Configuration

Set via `kv_connector_extra_config` in `--kv-transfer-config`[^nixl-lease]:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `kv_lease_duration` | 30s | Initial P lease; heartbeat interval (`duration // 6`) and extension (`duration * 2 // 3`) derive automatically. |
| `decoder_kv_blocks_ttl` | 480s | Fixed TTL for D-cached blocks in bidirectional mode; not heartbeat-renewed. |

Producer example:

```bash
vllm serve <MODEL> \
  --kv-transfer-config '{
    "kv_connector": "NixlConnector",
    "kv_role": "kv_producer",
    "kv_connector_extra_config": {"kv_lease_duration": 60}
  }'
```

## Relationships

- Uses [vLLM Paged Attention Kernel](vllm-paged-attention-kernel.md) block storage that leased P-side blocks pin; this concept covers only the lease/heartbeat lifetime, not block layout.

## Coverage limits

- PR #41383 was cited as the introducing change but was not inspected; implementation details above come from the design document alone[^nixl-lease].
- Referenced `../features/disagg_prefill.md` (bidirectional transfer) and `../features/nixl_connector_usage.md` (full connector configuration) were not compiled in this ingest; bidirectional semantics and non-lease connector options beyond the two parameters above are outside this concept's verified scope.

[^nixl-lease]: NIXL KV Cache Lease Renewal — `../raw/vllm/design/nixl_kv_cache_lease.md`, motivation, lease lifecycle, notification transport, scheduler tracking, worker send/receive, bidirectional TTL, design decisions, and configuration sections.
