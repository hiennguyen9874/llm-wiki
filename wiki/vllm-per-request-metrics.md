---
type: Concept
title: vLLM Per-Request Metrics
description: Per-request timing metrics returned in API responses via --enable-per-request-metrics for billing, SLA monitoring, and latency analysis.
tags: [vllm, metrics, observability, serving]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: per-request-metrics
    resource: ../raw/vllm/features/per_request_metrics.md
    title: Per-Request Metrics
---

vLLM can return per-request timing metrics directly in API responses when the server is started with `--enable-per-request-metrics`, complementing the server-aggregated Prometheus metrics at `/metrics` for billing, SLA monitoring, and individual-request latency analysis[^per-request-metrics].

## Enabling

Start the server with `--enable-per-request-metrics`; supported API responses then include a `metrics` object for each attributable request[^per-request-metrics]:

```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct --enable-per-request-metrics
```

At high concurrency, computing per-request metrics may introduce non-negligible CPU overhead; benchmark the specific workload before enabling in production[^per-request-metrics].

Per-request metrics require server-side statistics logging, which is on by default. vLLM rejects `--enable-per-request-metrics` when `--disable-log-stats` is also set[^per-request-metrics].

## Response fields

| Field | Description |
| --- | --- |
| `time_to_first_token_ms` | Time from when the request was scheduled until the first output token was generated (TTFT). |
| `generation_time_ms` | Decode time: first output token to last output token. Excludes queue wait and prefill/TTFT. |
| `queue_time_ms` | Time spent waiting in the scheduler queue before processing began. |
| `mean_itl_ms` | Mean inter-token latency during decode. `null` for single-token responses. |
| `tokens_per_second` | Output-token throughput over the inference interval (scheduling to last output token). Includes prefill, so it reflects end-to-end generation speed rather than pure decode speed. |

All fields are `null` when the underlying timing data is unavailable for that request[^per-request-metrics].

## Single-sequence scope

Timing metrics describe a single generation stream, so they are only returned when the request maps to exactly one[^per-request-metrics]:

- For chat/completions with `n > 1`, the `metrics` object is `null` because the timing data reflects only one of the `n` sequences and cannot be accurately attributed to the request as a whole. Token usage (`prompt_tokens`, `completion_tokens`) remains accurate.
- For `/v1/completions` with multiple prompts, metrics are likewise omitted because timing cannot be attributed to a single prompt's generation.

## Retrieval

Non-streaming clients read `metrics` from the response object alongside `usage` (for example via `response.model_extra.get("metrics")` in the OpenAI client)[^per-request-metrics].

In streaming responses, metrics are attached to the final usage chunk sent after all content chunks. That chunk is only emitted when usage reporting is enabled with `stream_options.include_usage: true`, or forced server-side with `--enable-force-include-usage`[^per-request-metrics].

Per-request metrics are available on both `/v1/chat/completions` and `/v1/completions` using the same `metrics` response field[^per-request-metrics].

## Relationships

- Uses [vLLM Metrics and Observability](vllm-metrics.md) — the `metrics` response field gives per-request values for one request, while `/metrics` exposes server-level histograms such as `vllm:time_to_first_token_seconds` aggregated across all requests.
- Uses [vLLM Entrypoints](vllm-entrypoints.md) — the flag-gated `metrics` field is an online-serving (`vllm serve`) response behavior for OpenAI-compatible chat and completions endpoints.
- [vLLM Per-Request Speculative Decoding Acceptance Metrics](vllm-per-request-spec-decode-metrics.md) — speculative-decoding extension under `metrics.speculative_decoding` via `--per-request-spec-decode-metrics`, sharing the `metrics` object, single-sequence scope, and streaming behavior described here.

[^per-request-metrics]: Per-Request Metrics — `../raw/vllm/features/per_request_metrics.md`, enabling flag, response format and field definitions, single-sequence and multi-prompt suppression, streaming usage-chunk behavior, completions coverage, Prometheus relationship, overhead note, `--disable-log-stats` conflict, and speculative-decoding pointer.
