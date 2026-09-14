---
type: Concept
title: vLLM Chunked Prefill
description: Default-on decode-prioritized prefill chunking with max_num_batched_tokens tuning for ITL, TTFT, and throughput.
tags: [vllm, chunked-prefill, scheduling, throughput, latency]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: opt-chunked
    resource: ../raw/vllm/configuration/optimization.md
    title: Optimization and Tuning
---

In vLLM V1 chunked prefill is enabled by default whenever possible, processing large prefills in smaller chunks batched with decode requests to balance compute-bound prefill and memory-bound decode work[^opt-chunked].

## Scheduling policy

With chunked prefill enabled the scheduler prioritizes decode requests: it batches all pending decode requests before scheduling any prefill, then schedules pending prefills within the remaining `max_num_batched_tokens` budget, automatically chunking a prefill that does not fit[^opt-chunked].

Benefits[^opt-chunked]:

- Better inter-token latency and generation decode because decodes are prioritized.
- Better GPU utilization by colocating compute-bound prefill and memory-bound decode in the same batch.

## Performance tuning

Tune with `max_num_batched_tokens`[^opt-chunked]:

- Smaller values (e.g. 2048) improve ITL because fewer prefills slow down decodes.
- Higher values improve time-to-first-token because more prefill tokens run per batch.
- For optimal throughput set `max_num_batched_tokens > 8192`, especially for smaller models on large GPUs.
- Setting `max_num_batched_tokens` equal to `max_model_len` approximates the V0 default scheduling policy, except decodes are still prioritized.

Example[^opt-chunked]:

```python
from vllm import LLM

llm = LLM(model="meta-llama/Llama-3.1-8B-Instruct", max_num_batched_tokens=16384)
```

## Disabled constraint

When chunked prefill is disabled, `max_num_batched_tokens` must be greater than `max_model_len`; if it is smaller, vLLM may crash at server startup[^opt-chunked].

## Relationships

- Uses [vLLM Request Preemption](vllm-request-preemption.md) — sibling scheduler pressure valve when KV space is insufficient; both are tuned via `max_num_batched_tokens` and `max_num_seqs`.
- Uses [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) — separate prefill and decode instances as an alternative to hand-tuning chunked-prefill chunk size for tail ITL.
- Uses [vLLM Multimodal Data Processing](vllm-multimodal-processing.md) — placeholder-to-input correspondence enabling chunked prefill for multimodal prompts.
- Uses [vLLM Prefix Caching](vllm-prefix-caching.md) — complementary reuse optimization for repeated prompt prefixes.

## Coverage limits

- Cited chunked-prefill papers (`arxiv.org/pdf/2401.08671`, `arxiv.org/pdf/2308.16369`) were not inspected beyond the source summary[^opt-chunked].

[^opt-chunked]: Optimization and Tuning — `../raw/vllm/configuration/optimization.md`, Chunked Prefill section covering default-on decode-first scheduling, `max_num_batched_tokens` ITL/TTFT/throughput guidance with 2048/8192/`max_model_len` rules, Python example, and disabled-mode `> max_model_len` crash constraint.
