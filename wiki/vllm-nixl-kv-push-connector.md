---
type: Concept
title: vLLM NIXL Push-Mode KV Transfer
description: Push-based disaggregated prefill/decode where prefill WRITEs KV directly into decode's pre-allocated blocks via a dedicated writer thread and PUSH_REG registrations.
tags: [vllm, kv-cache, disaggregated-prefill, nixl, push-mode]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T15:50:00Z }
sources:
  - id: nixl-push
    resource: ../raw/vllm/design/nixl_kv_push_connector.md
    title: NIXL push-mode KV transfer
---

`NixlPushConnector` is a push-based alternative to the default pull-based NIXL connector: instead of decode (D) READing KV from prefill (P) after prefill completes, P WRITEs KV blocks directly into D's pre-allocated memory via `NIXL WRITE`, reusing the pull-mode handshake, NIXL agent setup, and metadata path wherever possible[^nixl-push].

## Pull versus push

- **Pull (default):** D reads KV blocks from P via `NIXL READ` after prefill completes.
- **Push:** D pre-allocates blocks and registers them with P via `PUSH_REG`; P WRITEs finished blocks into D's GPU memory and sends a completion notification[^nixl-push].

## End-to-end flow

1. Proxy splits the request into a prefill leg (`do_remote_decode=True`) and a decode leg (`do_remote_prefill=True`)[^nixl-push].
2. D scheduler allocates blocks, stashes registration data, arms a watchdog, and emits `meta.push_registrations`; D writer thread sends `PUSH_REG:<msgpack>` to P via `send_notif`[^nixl-push].
3. P scheduler stashes finished-block IDs on `request_finished` and emits `meta.push_finished_blocks`; P writer thread stages them[^nixl-push].
4. P writer matches registrations against finished blocks, ensures the P→D handshake, issues `NIXL WRITE` direct to D GPU, then sends a completion notification[^nixl-push].
5. D worker drains completion notifications via `_pending_completion_notifs`, marks receive-done, and reports `finished_recving`; D scheduler clears the watchdog[^nixl-push].
6. P worker drains `_sending_transfers`, queues eviction, and reports `finished_sending`; P scheduler frees the lease[^nixl-push].

## Writer thread and wake model

`NixlPushConnectorWorker` adds one dedicated background thread per worker (per TP rank), named `nixl-push-writer`, owning all push-specific NIXL operations on its rank: `get_new_notifs`, `send_notif` for `PUSH_REG` and per-WRITE completion notifs, and `make_prepped_xfer` / `transfer` for the WRITE itself. Heartbeats still go out from the engine main thread via base-worker `start_load_kv` plumbing[^nixl-push].

The writer blocks on `_push_writer_wake` when idle and is woken by[^nixl-push]:

- `start_load_kv` (worker main thread, once per engine step) — only when `meta.push_registrations` or `meta.push_finished_blocks` is non-empty.
- `get_finished` (worker main thread, once per engine step) — always, so the writer drains inbound notifs (D heartbeats, WRITE completions, late `PUSH_REG`) even with no new metadata.
- Handshake-completion callbacks (background executor) — D→P handshake re-enqueues onto `_reg_send_inbox`; P→D handshake re-enqueues the matched `(req_id, blocks, reg_data)` onto `_deferred_push_inbox`. Neither `send_notif` nor WRITE may run off the writer thread. Failed handshakes fail or drop instead of re-enqueueing.

The writer also self-polls every `_PUSH_WRITER_POLL_INTERVAL_MS = 1.0` ms while P-side finished blocks wait unmatched, and stops when `get_finished` enqueues onto `_evict_finished_inbox` on P-side completion[^nixl-push].

## Matching and request-ID normalization

Writer-local tables, each single-consumer (the writer)[^nixl-push]:

| Table | Holds |
|-------|-------|
| `_pending_d_registrations` | D registrations from a remote D, waiting for P's blocks |
| `_push_finished_blocks` | P blocks staged by the scheduler, waiting for a remote D registration |

Either side can arrive first; the writer matches in both directions. Matching tries exact `request_id` first, then falls back to `get_base_request_id` stripping the trailing per-engine random suffix. The fallback exists because the proxy hands the same `X-Request-Id` to both legs (same `cmpl-<uuid>-<index>` form, differing only by the 8-hex suffix from `input_processor.assign_request_id`), preserving the completion index so multi-prompt sub-requests stay distinct, and working whether or not `VLLM_DISABLE_REQUEST_ID_RANDOMIZATION` is set[^nixl-push].

Replay queues with two producers (engine main thread plus handshake callback) are `_reg_send_inbox` and `_deferred_push_inbox`; remaining cross-thread queues have one producer[^nixl-push].

## Wire format

Push registration is a NIXL notification `PUSH_REG:<msgpack-encoded dict>` with fields set by D: `request_id` (D's own vLLM request id; match key echoed in completion), `decode_engine_id`, `decode_host`, `decode_port`, `decode_tp_size`, `local_block_ids` (per-group lists of D logical blocks, preallocated), plus `remote_engine_id`, `remote_host`, `remote_port`, `remote_tp_size` for the P-side handshake[^nixl-push].

D ships logical block ids; P expands them to physical ids at WRITE-submission time using the handshake-learned `remote_physical_blocks_per_logical` ratio, matching the pull-mode contract. The P→D completion notif reuses the pull-mode `<request_id>:<tp_size>` format, so D-side accounting is unchanged[^nixl-push].

## Scheduler responsibilities

`NixlPushConnectorScheduler` extends the base scheduler[^nixl-push]:

- **D side:** `update_state_after_alloc` stashes registration data in `_push_pending_registrations` and arms `_push_registration_deadlines`; `build_connector_meta` drains into `meta.push_registrations`, dropping expired entries with a warning.
- **P side:** `request_finished` stashes IDs in `_finished_request_blocks` (lease plus `has_pending_push_work`) and `_newly_finished_push_blocks` (next worker step via `meta.push_finished_blocks`).
- **Both sides:** `has_pending_push_work` keeps the engine loop stepping while push state is in flight, guaranteeing at least one writer wake per step.
- `update_connector_output`: `finished_sending` (P) clears the lease entry; `finished_recving` (D) clears the watchdog deadline.

## Timeouts and watchdogs

- **D-side registration watchdog** (`_push_registration_deadlines`): if no push completion arrives within `push_registration_timeout` seconds (defaults to `decoder_kv_blocks_ttl`), `build_connector_meta` drops the stale registration with a warning and stops resending. The request stays in `_reqs_need_recv`; the engine request-level abort path (or proxy/HTTP timeout) ultimately fails it[^nixl-push].
- **P-side block lease** (`_kv_lease_duration`, same as pull mode): `request_finished` sets expiry in `_reqs_need_send`; `update_connector_output(finished_sending=...)` clears it on successful WRITE. Stale leases are reaped by base-worker `get_finished`, which enqueues eviction onto `_evict_finished_inbox` so the writer stops self-polling[^nixl-push].

## Failure handling

- **D handshake failure or `send_notif` failure for PUSH_REG:** `_handle_failed_transfer(rid, None)` marks D's pre-allocated blocks invalid and enqueues onto `_failed_recv_reqs`; next `get_finished` reports a failed recv, same as pull mode[^nixl-push].
- **P handshake failure before WRITE:** done-callback logs `push_handshake_failed` and drops without re-queueing; deliberately no `_handle_failed_transfer` (no `_recving_metadata` entry on the producer side). P blocks are reclaimed by lease expiry, D registration by watchdog[^nixl-push].
- **P WRITE-submission failure:** release the WRITE handle if any, bump `xfer_stats.record_failed_transfer()`, and drop the outbound WRITE without calling `_handle_failed_transfer` (a P-local id in `_failed_recv_reqs` would trip the base-worker `get_finished` assertion). D's watchdog handles the missing completion[^nixl-push].

## Relationships

- Uses [vLLM NIXL KV Cache Lease Renewal](vllm-nixl-kv-lease.md) lease, heartbeat, and completion-notification machinery; this concept covers only the push WRITE path, matching tables, and watchdogs.
- Uses [vLLM Paged Attention Kernel](vllm-paged-attention-kernel.md) block storage that push registrations pin and WRITEs fill; this concept covers only transfer, not block layout.

## Coverage limits

- Pull-mode handshake, agent setup, and metadata internals are reused but not re-documented here; only push-specific threading, queues, and scheduling interactions were compiled.
- Implementation code, PRs, and `nixl_connector_usage` / `disagg_prefill` feature docs were not inspected in this ingest; operational configuration beyond `push_registration_timeout`, `decoder_kv_blocks_ttl`, and `_kv_lease_duration` is outside verified scope.

[^nixl-push]: NIXL push-mode KV transfer — `../raw/vllm/design/nixl_kv_push_connector.md`, high-level flow, threads and wake model, writer-local matching tables, wire format, scheduler responsibilities, timeouts and watchdogs, and failure handling sections.
