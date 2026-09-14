---
type: Concept
title: SGLang Observability
description: SGLang observability covering Prometheus metrics, request logging, request dump and replay, and crash-dump debugging.
tags: [sglang, observability, prometheus, debugging]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: sgl-observability
    resource: ../raw/sglang/advanced_features/observability.mdx
    title: Observability
---

SGLang combines opt-in Prometheus metrics, opt-in request logging, explicit request dump and replay for benchmarking, and crash dumps of the pre-crash window for post-mortem replay[^sgl-observability].

## Production metrics

Enable Prometheus metrics with `--enable-metrics` when launching the server, then query them from `/metrics`[^sgl-observability]:

```bash
curl http://localhost:30000/metrics
```

## Logging

By default SGLang does not log any request contents[^sgl-observability]. Enable request logging with `--log-requests` and control verbosity with `--log-request-level`[^sgl-observability].

## Request dump and replay

Dump all requests and replay them later for benchmarking or other purposes[^sgl-observability].

Start dumping by sending a configuration request to a running server[^sgl-observability]:

```bash
python3 -m sglang.srt.managers.configure_logging --url http://localhost:30000 --dump-requests-folder /tmp/sglang_request_dump --dump-requests-threshold 100
```

The server dumps requests into a pickle file for every 100 requests[^sgl-observability]. Replay a request dump with `scripts/playground/replay_request_dump.py`[^sgl-observability].

## Crash dump and replay

Crash dumping preserves all requests from the 5 minutes before a crash, so the failure can be replayed and debugged later[^sgl-observability].

Enable it with[^sgl-observability]:

```bash
# server launch flag
--crash-dump-folder /tmp/crash_dump
```

Replay a crash dump with `scripts/playground/replay_request_dump.py`[^sgl-observability].

## Relationships

- Uses [vLLM Metrics and Observability](vllm-metrics.md) — companion Prometheus and logging observability for comparing SGLang's metrics endpoint, request logging, and dump/replay workflow against vLLM's collection architecture, publishers, and metric set.

## Coverage limits

- The detailed metric catalog in the linked Production Metrics reference and the tracing schema in the linked Production Request Tracing reference were not present in `raw/` and were not compiled here; this concept covers only the `--enable-metrics` enablement and `/metrics` query stated in this source[^sgl-observability].
- Request-log verbosity levels, output formats, and targets in the linked server-arguments Logging section were not compiled here; this concept covers only `--log-requests` enablement, default-off request-content logging, and `--log-request-level` verbosity control[^sgl-observability].
- Dump-file schema, replay-script options, retention, privacy handling of logged request contents, and performance overhead were not specified in this source[^sgl-observability].

[^sgl-observability]: Observability — `../raw/sglang/advanced_features/observability.mdx`.
