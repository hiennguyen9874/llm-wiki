---
type: Concept
title: vLLM Metrics and Observability
description: V1 metrics collection, Prometheus and logging publishers, interval definitions, and deprecation and future-work policy for vLLM observability.
tags: [vllm, metrics, observability, prometheus]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: metrics
    resource: ../raw/vllm/design/metrics.md
    title: Metrics
---

vLLM v1 collects engine timing events in the engine core, computes request intervals and aggregates in the frontend API server, and publishes through logging and Prometheus publishers with a `vllm:` prefix[^metrics].

## Objectives and categories

Objectives are comprehensive engine- and request-level coverage for production monitoring, Prometheus-first integration, and log output for ad-hoc testing and debugging[^metrics].

Mental model: server-level metrics explain request-level metrics[^metrics]:

- **Server-level:** global engine state and performance, typically Prometheus Gauges or Counters.
- **Request-level:** per-request size and timing characteristics, typically Prometheus Histograms and often the SRE SLOs.

## V1 metric set

Exposed via Prometheus-compatible `/metrics` with the `vllm:` prefix[^metrics]:

- Gauges: `num_requests_running`, `kv_cache_usage_perc`.
- Counters: `prefix_cache_queries`, `prefix_cache_hits`, `prompt_tokens_total`, `generation_tokens_total`, `request_success_total` by finish reason.
- Histograms: `request_prompt_tokens`, `request_generation_tokens`, `time_to_first_token_seconds`, `inter_token_latency_seconds`, `e2e_request_latency_seconds`, `request_prefill_time_seconds`, `request_decode_time_seconds`.

A reference Prometheus plus Grafana example defines the especially important subset, including e2e latency buckets, prompt/generation tokens, inter-token latency / TPOT, TTFT, running/waiting/swapped request counts, KV usage, prompt/generation lengths, finished-request counts by `stop` versus `length`, queue time, prefill/decode time, and max generation tokens[^metrics].

## Collection architecture

Performance goal is to move computation out of the engine-core inner loop into the frontend outer loop, ideally `AsyncLLM.output_handler_loop`, which overlaps GPU execution[^metrics].

- Engine core runs scheduler and model execution; frontend derives metrics from `EngineCoreOutputs` returned per iteration[^metrics].
- Engine core attaches scheduler stats, such as scheduled versus waiting request counts after the last scheduler pass, to `EngineCoreOutputs`[^metrics].
- Engine core records monotonic timestamps for per-request events; frontend calculates intervals only from same-process monotonic pairs[^metrics].

Monotonic-clock rule: use `time.monotonic()`, not wall-clock time, for intervals because wall clocks shift under NTP; monotonic references differ per process, so intervals must compare timestamps from the same process[^metrics].

## Events and intervals

Engine-core events[^metrics]:

- `QUEUED`: received by engine core and added to scheduler queue.
- `SCHEDULED`: first scheduled for execution, updated on rescheduling.
- `PREEMPTED`: returned to waiting queue to free capacity; restarts prefill when rescheduled.
- `NEW_TOKENS`: output included in `EngineCoreOutput` was generated; one timestamp per `EngineCoreOutputs` because it is common to the iteration.

Calculated intervals[^metrics]:

- Queue: `QUEUED` to most recent `SCHEDULED`.
- Prefill: most recent `SCHEDULED` to subsequent first `NEW_TOKENS`.
- Decode: first post-`SCHEDULED` to last `NEW_TOKENS`.
- Inference: most recent `SCHEDULED` to last `NEW_TOKENS`.
- Inter-token: between successive `NEW_TOKENS`.

Frontend TTFT and end-to-end definitions differ from pure engine-core intervals[^metrics]:

- TTFT is measured from frontend `arrival_time`, when tokenization begins, to first-token iteration, thereby including input-processing time.
- End-to-end latency is frontend `arrival_time` to frontend receipt of the final token.
- Per-iteration frontend stats include new tokens generated, prompt tokens from completed prefills, queue intervals for newly scheduled requests, prefill intervals and TTFT for completed prefills, and inter-token intervals for all requests in the iteration.
- Completed requests additionally record inference/decode intervals and end-to-end latency.

Preemption semantics: decode preemption, where generated tokens are reused, affects inter-token, decode, and inference intervals; prefill preemption affects TTFT and prefill intervals[^metrics].

## KV cache residency metrics

Sampled histograms describe KV-block lifetime and reuse; `--kv-cache-metrics-sample` keeps overhead small[^metrics]:

- `vllm:kv_block_lifetime_seconds`: allocation to eviction.
- `vllm:kv_block_idle_before_evict_seconds`: last touch to eviction.
- `vllm:kv_block_reuse_gap_seconds`: gaps between consecutive touches.

Engine core ships only raw eviction events via `SchedulerStats`; frontend converts them to Prometheus observations and exposes the same data through `LLM.get_metrics()` when logging is enabled. Joint lifetime versus idle-time views reveal stranded cache or long-pinned prompts[^metrics].

## Publishing

`LoggingStatLogger` emits an `INFO` message every 5 seconds with running/waiting counts, GPU cache usage, prompt and generation throughput over the window, and prefix-cache hit rate over the most recent 1k block queries[^metrics].

`PrometheusStatLogger` serves `/metrics` for Prometheus scraping and Grafana graphing[^metrics]:

- Counter: monotonically increasing lifetime value, for example total generated tokens.
- Gauge: up/down value, for example currently scheduled requests.
- Histogram: bucketed sample counts, for example TTFT thresholds.
- Every vLLM metric carries a `model_name` label; histogram bucket choice remains an open refinement problem[^metrics].

## Special metrics

- `vllm:cache_config_info`: startup-only `CacheConfig` key/value data exposed through a Gauge set to 1 with `multiprocess_mode="mostrecent"`, because `prometheus_client` does not support Info metrics in multiprocess mode[^metrics].
- `vllm:lora_requests_info`: Gauge holding current wall-clock time, updated every iteration, with comma-separated per-adapter running/waiting counts plus static `max_lora`; the source calls the string encoding misguided and says a redesign should use labels and coordinate with known downstream users before deprecating[^metrics].
- Prefix cache: expose `queries` and `hits` counters and let users compute hit rate in PromQL such as `rate(hit[5m]) / rate(total[5m])`, rather than publishing a hit-rate gauge; logging computes hit rate over the most recent 1k queries[^metrics].

## Infrastructure history

- Prometheus support moved from `aioprometheus` to `prometheus_client`; HTTP metrics were briefly lost with `MetricsMiddleware` and reinstated with `prometheus_fastapi_instrumentator`, exposing `http_requests_total`, request/response size counts, and duration counts per handler and method[^metrics].
- Metrics collection moved from engine core with multiprocess export to the API server; multiprocess mode is now needed only when `--api-server-count > 1`[^metrics].
- Built-in `python_*` and `process_*` metrics from `prometheus_client` are unavailable when `--api-server-count > 1`; the source questions their value because they do not aggregate across all vLLM processes[^metrics].

## Deprecation and legacy cleanup

Deprecation guidance: be cautious because removal can surprise users, add a prominent deprecation notice to the `/metrics` help string, list deprecations in docs and release notes, and consider hiding deprecated metrics behind a CLI flag before deletion, following the project deprecation policy[^metrics]. The `avg_prompt_throughput_toks_per_s` deprecate-remove-then-user-notice sequence is given as a cautionary example[^metrics].

Legacy items identified for removal or consolidation[^metrics]:

- `vllm:tokens_total`: added but apparently never implemented; removable.
- Queue-time duplication: `vllm:time_in_queue_requests` versus later `vllm:request_queue_time_seconds`; the latter feeds the Grafana dashboard, so deprecate or remove the former.
- Prefix-cache hit-rate gauge: replaced by queries/hits counters.
- `vllm:num_requests_swapped` and `vllm:cpu_cache_usage_perc`: tied to removed v1 CPU-swap preemption and `--swap-space`; v1 favors prefix caching plus preemption and recompute. Related cleanup removed `SequenceGroup` beam-search sharing from the core and moved beam search out, leaving parallel sampling `n > 1` support for later work.

## Future work

- Parallel sampling: add `vllm:request_params_n` and `vllm:request_max_num_generation_tokens` alongside parallel-sampling support; without `n > 1`, the latter equals `request_generation_tokens`[^metrics].
- Speculative decoding: revisit draft acceptance rate, efficiency, accepted/draft/emitted token metrics as ngram and other v1 speculative methods land; prefer accepted and draft counters over a precomputed acceptance-rate gauge, as with prefix-cache hit rate[^metrics].
- Autoscaling and load balancing: no agreed saturation signal yet; discussion centers on detecting the inflection where higher request rate no longer raises throughput but adds latency, informed by Kubernetes serving-group proposals and vLLM autoscaling issues[^metrics].
- Naming: revisit colon use because Prometheus reserves colons for recording rules, inconsistent unit suffixes, and `_total` handling for OpenMetrics compatibility[^metrics].
- Addition caution: new metrics are easy to add but hard to remove, can cost production performance when enabled by default, and increase long-term maintenance; proposals include TGI metrics, autoscaling-driven metrics, and OpenTelemetry GenAI semantic conventions[^metrics].

## Tracing boundary

Tracing is treated as separate from metrics. vLLM supports OpenTelemetry tracing via `--oltp-traces-endpoint` and `--collect-detailed-traces`, with user and product documentation maintained outside this design[^metrics].

The OTel-gated `vllm:model_forward_time_milliseconds` and `vllm:model_execute_time_milliseconds` histograms measure model-forward time versus fuller execute time including worker sync and sampling. They appear as GenAI latency attributes, overlap existing inference/decode metrics, may carry blocking-operation overhead, and are left to a separate OTel decision[^metrics].

## Relationships

- Uses [vLLM V1 Process Architecture](vllm-v1-process-architecture.md) — metrics move work from the engine-core inner loop to the API-server outer loop and depend on API-server versus engine-core counts and multiprocess behavior.
- Uses [vLLM Prefix Caching](vllm-prefix-caching.md) — prefix-cache queries and hits counters are the Prometheus form of the hit-rate mechanism that concept implements.
- Uses [vLLM LoRA Resolver Plugins](vllm-lora-resolver-plugins.md) — per-adapter running and waiting counts in `lora_requests_info` describe adapters discovered through resolver plugins.

## Coverage limits

- Interval diagrams for the common, preempted-decode, and preempted-prefill cases in `../raw/vllm/assets/design/metrics/` were inspected and are reflected in the events, intervals, and preemption sections[^metrics].
- Referenced user docs, Grafana and OpenTelemetry examples, serving and contributing docs, and linked GitHub issues, PRs, discussion comments, and external Kubernetes, OpenTelemetry, TGI, and IBM materials were not inspected; claims depending on them carry the design document's authority only[^metrics].

[^metrics]: Metrics — `../raw/vllm/design/metrics.md`, objectives, background, v1 metrics, Grafana dashboard, client-library and multiprocess history, collection and interval design, frontend stats, KV residency, logging and Prometheus publishing, cache-config/LoRA/prefix metrics, deprecation and legacy cleanup, future work, and tracing boundary sections.
