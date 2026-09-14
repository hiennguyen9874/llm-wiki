---
type: Concept
title: vLLM Per-Request Speculative Decoding Acceptance Metrics
description: Per-request speculative-decoding acceptance metrics in vLLM responses via --per-request-spec-decode-metrics for mean acceptance length and draft distribution.
tags: [vllm, speculative-decoding, metrics, observability]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: spec-acceptance
    resource: ../raw/vllm/features/speculative_decoding/acceptance_metrics.md
    title: Per-Request Acceptance Metrics
---

vLLM can report per-request speculative-decoding acceptance metrics under `metrics.speculative_decoding` when speculative decoding is enabled, letting a client compute mean acceptance length and accepted-draft-length distribution for an individual request as a complement to server-aggregated spec-decode counters at `/metrics`[^spec-acceptance].

> Experimental: `metrics.speculative_decoding` may change shape in a future release; pin to a vLLM version if depending on it[^spec-acceptance].

## Enabling

Start the server with `--per-request-spec-decode-metrics` set to `summary` or `detailed` (default `none`)[^spec-acceptance]:

```bash
vllm serve <target-model> \
  --speculative-config '{"method": "ngram", "num_speculative_tokens": 3, "prompt_lookup_min": 1, "prompt_lookup_max": 3}' \
  --per-request-spec-decode-metrics summary
```

| Level | Behavior |
| --- | --- |
| `none` (default) | No collection; responses are unchanged. |
| `summary` | Acceptance metrics per request. |
| `detailed` | `summary` plus ordered per-step arrays. |

Collection is gated at the source: with `none`, nothing is accumulated[^spec-acceptance].

## Response format

Acceptance metrics share the top-level `metrics` object with timing per-request metrics — `metrics.speculative_decoding` sits alongside the timing fields. Like timing, they describe a single generation stream, so they are reported only for single-sequence requests and are `null` for `n > 1`[^spec-acceptance].

Summary fields:

| Field | Description |
| --- | --- |
| `mean_acceptance_length` | Mean tokens emitted per verification step, including the bonus token: `1 + num_accepted_draft_tokens / num_spec_steps`. Ranges from `1.0` (nothing accepted) to `num_spec_tokens + 1`[^spec-acceptance]. |
| `draft_acceptance_rate` | Fraction of proposed draft tokens accepted: `num_accepted_draft_tokens / num_draft_tokens`[^spec-acceptance]. |
| `acceptance_histogram` | Dense list of length `num_spec_tokens + 1`; index `j` is the number of steps that accepted exactly `j` draft tokens. Excludes the always-accepted bonus token[^spec-acceptance]. |
| `num_spec_steps` | Number of verification steps for this request (the sum of the histogram)[^spec-acceptance]. |
| `num_accepted_draft_tokens` | Total accepted draft tokens, excluding bonus tokens[^spec-acceptance]. |
| `num_draft_tokens` | Total proposed draft tokens, after subtracting drafts invalidated by structured-output constraints[^spec-acceptance]. |
| `num_spec_tokens` | Configured `num_speculative_tokens` (`k`), i.e. maximum draft length per step[^spec-acceptance]. |

With `detailed`, two ordered arrays are added, one entry per verification step[^spec-acceptance]:

| Field | Description |
| --- | --- |
| `per_step_accepted` | Accepted draft count at each step. |
| `per_step_drafted` | Proposed draft count at each step. Records effective proposal length per step, so variable-length drafting (e.g. adaptive speculation) is represented without a schema change. |

`metrics.speculative_decoding` is present whenever `--per-request-spec-decode-metrics` is `summary`/`detailed`, speculative decoding is enabled, and `n == 1` (with an all-zero histogram if the request drafted nothing). It is `null` otherwise[^spec-acceptance].

## Streaming

In streaming responses, `metrics` (including `speculative_decoding`) rides the final usage chunk, which is only emitted when usage reporting is enabled — set `stream_options.include_usage: true` or start the server with `--enable-force-include-usage`[^spec-acceptance].

## Relationship to Prometheus metrics

Per-request fields are the individual-request counterpart of server-aggregated spec-decode counters at `/metrics`. Summed across the single-sequence requests that report them, they reconcile with aggregate counters (which also count `n > 1` requests, so totals match only for all-`n == 1` workloads)[^spec-acceptance]:

| Per-request field (summed) | Prometheus counter |
| --- | --- |
| `num_spec_steps` | `vllm:spec_decode_num_drafts_total` |
| `num_draft_tokens` | `vllm:spec_decode_num_draft_tokens_total` |
| `num_accepted_draft_tokens` | `vllm:spec_decode_num_accepted_tokens_total` |

## Relationships

- Uses [vLLM Per-Request Metrics](vllm-per-request-metrics.md) — `speculative_decoding` shares the top-level `metrics` response object with timing fields, inherits single-sequence (`n == 1`) suppression and final-usage-chunk streaming behavior.
- Uses [vLLM Metrics and Observability](vllm-metrics.md) — summed per-request `num_spec_steps`, `num_draft_tokens`, and `num_accepted_draft_tokens` reconcile with the server-aggregated `vllm:spec_decode_*` Prometheus counters.
- Uses [vLLM Entrypoints](vllm-entrypoints.md) — flag-gated `metrics.speculative_decoding` is an online-serving (`vllm serve`) response behavior for OpenAI-compatible endpoints.

[^spec-acceptance]: Per-Request Acceptance Metrics — `../raw/vllm/features/speculative_decoding/acceptance_metrics.md`, enabling flag and collection gating, summary/detailed response fields and formulas, presence and `n > 1` suppression, streaming usage-chunk behavior, and Prometheus counter mapping.
