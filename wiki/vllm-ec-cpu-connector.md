---
type: Concept
title: vLLM EC CPU Connector
description: Local CPU-tier encoder-cache offload with optional NIXL peer-to-peer transfer for disaggregated vision encoding.
tags: [vllm, multimodal, disaggregated-inference, encoder-cache]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: ec-cpu-connector
    resource: ../raw/vllm/features/ec_cpu_connector.md
    title: CPU EC Connector Usage Guide
---

`ECCPUConnector` extends the GPU encoder cache with a CPU tier: it offloads `encoder_cache[mm_hash]` into a shared `/dev/shm` mmap region for reuse across steps and requests, with GPU↔CPU copies on pooled CUDA streams asynchronous to model compute; setting `ec_enable_nixl: true` additionally enables peer-to-peer transfer where a consumer pulls an encoding directly from a producer's CPU tier over NIXL instead of recomputing it[^ec-cpu-connector].

## Prerequisites

- Requires the V2 model runner (`VLLM_USE_V2_MODEL_RUNNER=1`); construction raises `ValueError` otherwise[^ec-cpu-connector].
- Local CPU-tier offload (`ec_enable_nixl` unset or `false`) needs no extra packages — the gated-off code path (`cpu/connector.py`, `cpu/scheduler/`, `cpu/worker/`, `cpu/common.py`) imports no `nixl`/`zmq`/`msgspec`, enforced by `tests/v1/ec_connector/unit/test_no_nixl_imports.py`[^ec-cpu-connector].
- P2P NIXL mode (`ec_enable_nixl: true`) requires the `nixl` package (`nixl==1.3.2` in `requirements/kv_connectors.txt`, shared with `NixlConnector`); if unimportable the connector raises `RuntimeError` directing the operator to install `nixl` or remove the flag[^ec-cpu-connector].

## Local CPU tier

- Single-instance mode uses `ec_role="ec_both"`: the same process offloads to and reloads from the CPU tier[^ec-cpu-connector].
- The tier is one mmap region (`/dev/shm/vllm_ec_{instance_id}_dp{dp_rank}.mmap`) shared by every TP/PCP worker of the instance; only TP rank 0 / PCP rank 0 writes on save because all ranks hold identical encoder output[^ec-cpu-connector].
- Entries are keyed by `mm_hash`; `EmbeddingCache` evicts ready and unpinned entries FIFO when space is needed[^ec-cpu-connector].
- Each batched save/load runs on a pooled CUDA stream; completion is reported once the transfer's end event fires (`ECCPUWorker.build_connector_worker_meta` → `ECCPUScheduler.update_connector_output`), marking saved entries ready and unpinning loaded ones[^ec-cpu-connector].
- The region is unlinked from `/dev/shm` in `shutdown()`; cleanup after `SIGKILL` is best-effort and leaked files must be removed manually[^ec-cpu-connector].

## P2P NIXL roles

- Producer (`ec_role="ec_producer"`) offloads GPU→CPU only and serves consumer reads; this role alone enables `mm_encoder_only`, so `vllm_config.is_mm_encoder_only` is true and the language model, sampler, and pooler are skipped — pass `--mm-encoder-only` only for encoder-only execution independent of `ec_transfer_config`[^ec-cpu-connector].
- Consumer (`ec_role="ec_consumer"`) reloads CPU→GPU only, pulling encodings named in a request's `ec_transfer_params` before falling back to local encoding[^ec-cpu-connector].
- Intended for E/PD disaggregation or encoder/decoder-instance sharing[^ec-cpu-connector].

## Orchestration flow

1. A request finishes on the producer. `ECCPUConnector.request_finished()` returns, for each `mm_hash` still resident, `{mm_hash: {"metadata": {...}, "peer_host": str, "peer_port": int, "size_bytes": int}}`, surfaced as `ec_transfer_params` (`RequestOutput.ec_transfer_params` / `EngineCoreOutput.ec_transfer_params`). `metadata` carries the model-declared placeholder fields for an orchestrator that rewrites media into a metadata-only reference; the remaining keys are the connector's handle[^ec-cpu-connector].
2. Publication is atomic: an `mm_hash` the producer cannot serve — never saved because the region was full, or since evicted — is reported with empty `metadata` and no address, so the orchestrator leaves the media on the request and the consumer encodes locally[^ec-cpu-connector].
3. The orchestrator issues a follow-up request with the same `mm_hash` to a consumer, passing the producer's params through `SamplingParams.extra_args["ec_transfer_params"]`[^ec-cpu-connector].
4. On the consumer, `ECCPUScheduler.ensure_cache_available()` opens a ZMQ session to `(peer_host, peer_port)` per uncached `mm_hash`, sends `XferReq`, and on `OK` issues a consumer-initiated NIXL READ from the producer's mmap into its own; the request is deferred until the READ completes[^ec-cpu-connector].
5. `NACK_NOT_READY` (announced but GPU→mmap save not yet landed) releases the in-flight entry without recording failure and retries on a later step, costing latency rather than a recompute; any other NACK, ack timeout, read timeout, or peer disconnect discards the entry and falls back to local encoding, never blocking the request indefinitely[^ec-cpu-connector].

## Protocol

- Control plane is ZMQ: producer binds `ROUTER` on `VLLM_EC_SIDE_CHANNEL_HOST:VLLM_EC_SIDE_CHANNEL_PORT`; each consumer opens one `DEALER` per producer peer with heartbeating (2s interval, 4s timeout, 8s TTL). `XferReq`/`XferAck` are `msgspec` msgpack structs versioned by `EC_CONNECTOR_VERSION` (currently `1`); mismatch is NACKed[^ec-cpu-connector].
- Compatibility check is a SHA-256 hash over `(vllm_version, model, dtype, block_size_bytes)`; differing peers get `NACK_INCOMPAT`[^ec-cpu-connector].
- Ack statuses are `OK`, `NACK_MISSING`, `NACK_NOT_READY`, `NACK_INCOMPAT`, `NACK_VERSION`, `NACK_INTERNAL`; only `NACK_NOT_READY` is retryable, classified by `RETRYABLE_NACKS` in `cpu/protocol.py` alongside the wire vocabulary[^ec-cpu-connector].
- Data plane is NIXL with hardcoded `UCX` backend, consumer-initiated `READ` — the producer never pushes; the `XferAck` carries producer NIXL agent metadata so a consumer can recover a READ against a restarted producer without a fresh handshake[^ec-cpu-connector].
- Timeouts: consumer XferAck wait 2s; NIXL read 20s (then the destination is quarantined, not evicted, up to 60s to let unabortable DMA settle); producer releases an unclaimed pinned grant after a 30s pin lease[^ec-cpu-connector].

## Configuration

EC transfer is set via `--ec-transfer-config` or `VllmConfig.ec_transfer_config` (`ECTransferConfig`, `vllm/config/ec_transfer.py`)[^ec-cpu-connector]:

| Field | Default | Notes |
| --- | --- | --- |
| `ec_connector` | `None` | Use `"ECCPUConnector"`. |
| `ec_role` | `None` | Required when connector is set: `ec_producer` (GPU→CPU only), `ec_consumer` (CPU→GPU only), `ec_both` (both). |
| `ec_connector_extra_config` | `{}` | See below; includes `ec_enable_nixl`. |
| `engine_id` | random UUID4 | Names the NIXL agent when `ec_enable_nixl=True`. |
| `ec_connector_module_path` | `None` | Module path for out-of-tree connectors outside the built-in registry (`ECExampleConnector`, `ECCPUConnector`). |

`ec_connector_extra_config` reference[^ec-cpu-connector]:

| Key | Default | Notes |
| --- | --- | --- |
| `ec_cpu_bytes` | required | Total mmap size in bytes; raises `ValueError` if unset. Block count is `ec_cpu_bytes // block_size_bytes` where `block_size_bytes = hidden_dim * dtype.element_size()`; `hidden_dim` accounts for Qwen3-VL deepstack (`out_hidden_size * (1 + num_deepstack_layers)`). |
| `ec_enable_nixl` | `false` | Enables NIXL P2P in addition to local offload. Not type-coerced: string `"true"`/`"1"`/`"yes"` enables, anything else does not. |
| `consumer_ack_timeout_s` | `2.0` | Consumer `XferAck` wait. The producer answers from its scheduler step, so reply latency scales with the encoder's `--max-num-batched-tokens`; raise it when loaded-encoder steps exceed the timeout or consumers abandon grantable reads. |

Environment (read only when `ec_enable_nixl=True` on a producer with `ec_producer` or `ec_both`)[^ec-cpu-connector]:

| Variable | Default | Notes |
| --- | --- | --- |
| `VLLM_EC_SIDE_CHANNEL_HOST` | `localhost` | Producer `ROUTER` bind host; set to a routable address (e.g. pod IP) for multi-instance/multi-node P2P. |
| `VLLM_EC_SIDE_CHANNEL_PORT` | `5601` | Producer `ROUTER` bind port. |

## Limitations

- No eviction notification: a consumer only learns an encoding was evicted before consumption via `NACK_MISSING` and then recomputes locally[^ec-cpu-connector].
- A retried read releases destination blocks and reallocates them next step, so a slow-to-land producer save makes the consumer evict ready entries to win the same blocks back once per engine step[^ec-cpu-connector].
- Fallback to local encoding requires the media to still be on the request. Announcing only servable encodings keeps an orchestrator from rewriting media away for an unservable one, but an encoding lost *after* announcement — evicted between announcement and read — leaves a rewritten request with nothing to embed and fails in the worker's `sanity_check_mm_encoder_outputs`, because `ensure_cache_available()` can only defer, not fail, a request[^ec-cpu-connector].

## Relationships

- Uses [vLLM Disaggregated Encoder](vllm-disaggregated-encoder.md) — concrete `ECCPUConnector` implementation of the encoder-cache transfer leg that the disaggregated-encoder flow describes via `ExampleConnector`.
- Uses [vLLM Model Runner V2](vllm-model-runner-v2.md) — requires the V2 runner; construction fails otherwise.
- Uses [vLLM Custom Arguments](vllm-custom-arguments.md) — producer handles travel to the consumer in `SamplingParams.extra_args["ec_transfer_params"]`, the same out-of-spec request channel.

## Coverage limits

- Cited code paths (`cpu/connector.py`, `cpu/scheduler/`, `cpu/worker/`, `cpu/common.py`, `cpu/protocol.py`, `vllm/config/ec_transfer.py`), the no-NIXL-import test, `requirements/kv_connectors.txt`, and the external NIXL repository were not inspected; claims rest on the usage-guide prose[^ec-cpu-connector].
- No performance, TTFT, or sizing measurements were in the source; `ec_cpu_bytes` guidance is limited to the block-count formula above[^ec-cpu-connector].

[^ec-cpu-connector]: CPU EC Connector Usage Guide — `../raw/vllm/features/ec_cpu_connector.md`, covering CPU-tier mmap offload with pooled-stream `swap_blocks_batch` copies, `ec_both`/`ec_producer`/`ec_consumer` roles, `mm_hash` keying with FIFO eviction, V2-runner and `nixl` prerequisites, `ec_transfer_config` plus `ec_connector_extra_config` and side-channel environment reference, ZMQ control plane with versioned `XferReq`/`XferAck` and hash compatibility check, NIXL UCX READ data plane with restart recovery, orchestration flow with atomic publication and `NACK_NOT_READY` retry versus fallback, timeout and pin-lease values, and eviction, cleanup, and rewritten-request failure limits.
