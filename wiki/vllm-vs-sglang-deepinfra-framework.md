---
type: Synthesis
title: vLLM vs SGLang DeepInfra Decision Framework
description: DeepInfra workload-first framework for vLLM versus SGLang with benchmark-validity checks, prefix-reuse probe, and self-host versus managed-endpoint economics.
tags: [vllm, sglang, inference-serving, benchmarking, prefix-caching, cost]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T18:00:00Z }
sources:
  - id: deepinfra-vllm-sglang
    resource: ../raw/vllm-vs-sglang/index.md
    title: "vLLM vs SGLang: Performance, Features & Deployment Compared"
---

A DeepInfra comparison argues the engine question is secondary to two prior questions: whether published benchmarks measured your workload, and whether you should self-host GPUs at all. Its durable contribution is a workload-first triage — prefix-reuse ratio, batch shape, structured-output share, and model topology — plus a same-day TTFT probe and self-host break-even arithmetic, not a universal speed ranking[^deepinfra-vllm-sglang].

## Benchmark-validity checks

The source's central warning is that leaderboard deltas are usually non-transferable. A benchmark is usable only when releases are contemporaneous, flags are matched, and the request distribution matches yours[^deepinfra-vllm-sglang].

Two worked critiques carry the rule:

- AI Multiple's often-cited 16,215 tok/s (SGLang) versus 12,553 tok/s (vLLM) — a 29% gap on Llama 3.1 8B bf16, single H100 80GB, 1,000 prompts run ten times — pairs SGLang v0.2.3 with vLLM 0.11.0, releases roughly two years apart. The source treats the number as unable to rank either engine today, in either direction. The same writeup's GPU-memory-utilization 0.95 crash versus 0.8 success is framed as a tuning artifact, not an engine property[^deepinfra-vllm-sglang].
- RunPod's KV-cache-reuse figures — SGLang 35.0 tok/s versus vLLM 32.8 tok/s on 2x H100 with a 70B distill at 7k context — are single-stream decode rates for one reader, while AI Multiple's 16k tok/s figure is aggregate saturated-batch throughput. Both are labeled "tokens per second" but answer different questions: time-visible text for one session versus sessions absorbed before queueing. The source recommends its companion KPI breakdown over any leaderboard for chat-UI work[^deepinfra-vllm-sglang].

## Engine origins snapshot

Both engines have converged on continuous batching, chunked prefill, speculative decoding, structured generation, FP8 and INT4 quantization, tensor parallelism, and multi-LoRA; read the remaining differences as optimization center and ecosystem reach rather than feature presence[^deepinfra-vllm-sglang].

|  | vLLM | SGLang |
| --- | --- | --- |
| Origin optimization | PagedAttention KV paging; now table stakes everywhere | RadixAttention prefix reuse over a radix tree |
| Scheduler focus | V1 splits client layer from GPU execution loop over ZMQ so Python scheduling stops taxing decode at high concurrency; v0.25.0 made Model Runner V2 default for dense models | Zero-overhead batch scheduler in v0.4 overlapping CPU scheduling with GPU compute, cited at ~1.1x throughput |
| Cache contrast | Automatic prefix caching as hash-block lookup | Radix tree handling partial and branching overlap without declared-cacheable regions; suited to agent traces and multi-turn shape |
| Dated snapshot, 2026-07-14 | v0.25.1, 86,819 stars | v0.5.15.post1, 30,590 stars |
| Leans toward | Broad model and hardware coverage, day-one architecture support | Shared-prefix and structured workloads |

Star counts are framed as ecosystem reach and contributor breadth, not quality ranking[^deepinfra-vllm-sglang].

## Four workload signals

Ignore leaderboards and characterize local traffic first[^deepinfra-vllm-sglang]:

| Signal | What to compute | Why it decides |
| --- | --- | --- |
| Prefix reuse ratio | Share of input tokens in a prefix shared with another request | Coding agent replaying a 12k-token preamble can exceed 80% shared; a distinct-document summarizer sits near zero. Cached runs in the cited RunPod tests showed ~20% gain once hits landed; below ~20% reuse the signal stops discriminating. |
| Batch shape | Saturated offline queue versus bursty interactive traffic | Offline bulk work is an aggregate-throughput packing problem; low-concurrency interactive work is a time-to-first-token problem where scheduler overhead and prefill chunking dominate. Most teams run both shapes and measure one. |
| Structured output share | Fraction of calls under constrained decoding and schema churn | Constraint-compiler cost per unique schema is a real latency term; a few hot schemas hurt far less than per-request generated schemas. |
| Model topology | Dense versus large MoE placement | Dense Llama-3.3-70B-class shards predictably over tensor-parallel ranks; DeepSeek-V3.2 / Kimi-K2.6-class MoE adds expert parallelism, interconnect, and tuning surface; Qwen3-30B-A3B-class fits a single node. The model choice can move ops burden more than the engine. |

Choosing open weights is usually framed as right on price, with a pointer to re-check open-versus-proprietary capability and cost[^deepinfra-vllm-sglang].

## TTFT prefix-reuse probe

The source's same-day test avoids provisioning a GPU: stream the real 8k+ token preamble twice against a hosted endpoint and compare cold versus warm time to first token. Read the delta, not absolutes — warm collapsing to a fraction of cold means reusable prefix dominates and RadixAttention differentiates if self-hosted; a delta inside noise means cache behavior decides nothing and coverage plus familiarity should decide[^deepinfra-vllm-sglang].

The probe procedure is a TCP/TLS warmup with an unshared prompt, then one cold TTFT plus several warm TTFTs over the shared preamble, repeated five to ten times with medians. Three confounders are named: load-balanced replicas that never saw the prefix, cache aging over pauses, and concurrency pressure where prefix cache and active KV compete for the same HBM — a prefix resident at 4 concurrent requests can evict at 200. Measure at production concurrency or the hit rate will not transfer[^deepinfra-vllm-sglang].

Implementation detail is preserved only as method: the source script is Python with the OpenAI client against an OpenAI-compatible base URL, token budget 64, first-content-token timing, and a guard for empty final streaming chunks. The API token is read from the environment; no credential is stored[^deepinfra-vllm-sglang].

Tunable eviction policy and memory split are framed as the sharpest self-hosting argument — yours to control on owned hardware, opaque on a hosted endpoint[^deepinfra-vllm-sglang].

## Self-host versus managed-endpoint economics

Every engine comparison assumes GPUs are already decided; the source prices that assumption first, with explicit instruction to redo the math on own rates[^deepinfra-vllm-sglang]:

- Self-host reference: 8x H100-class node at $2/GPU-hr = $16/hr, ~$11,700/month, billed saturated or idle.
- Managed reference: $0.26/1M input, $0.38/1M output, $0.13/1M cached input tokens; at 4:1 input-to-output mix one unit (1M in + 250k out) costs $0.355.
- Break-even: ~33B input plus ~8B output tokens per month, i.e. roughly 12,000 input tok/s sustained around the clock — not peak. Diurnal bursty traffic at 10-20% utilization leaves most of the fixed node buying idle silicon. Cached-input pricing tilts further toward managed for prefix-heavy work.
- Uncounted cost: GPU memory tuning, kernel-regression chasing across releases, cold starts, autoscaling, and pager rotation; a managed OpenAI-compatible endpoint reduces a model swap to a string edit.

The source notes its own nine-provider latency/throughput spread for the same model family can swamp the engine delta, and points to its companion pricing and benchmark posts for live numbers rather than treating the above as fixed[^deepinfra-vllm-sglang].

## When self-hosting still wins

Three flips are named explicitly[^deepinfra-vllm-sglang]:

- Sustained saturation at tens of billions of tokens per month and high utilization; batch pipelines reach this faster than interactive products because arrival rate is controllable.
- Regulatory placement where work cannot leave a jurisdiction or VPC.
- Modification needs: custom kernels, self-trained draft models for speculative decoding, per-tenant hot-swapped LoRA adapters, or unlanded architectures. Here vLLM is framed as sooner with new-architecture support while SGLang is easier to reason about for scheduling and cache changes.

The middle path is common: self-host one saturated workload and route the long tail to an API, keeping the fixed node busy and the tail elastic[^deepinfra-vllm-sglang].

## Selection summary

Run in order; the answer usually falls out in a day[^deepinfra-vllm-sglang]:

- **SGLang** with measured high prefix reuse, multi-turn or agentic traffic on a stable preamble, heavy constrained decoding, and an owner for scheduling and cache behavior.
- **vLLM** for broad model and accelerator coverage, day-one architecture support, or mixed traffic with no dominant cache pattern.
- **Managed endpoint** for bursty utilization, sub-break-even volume, or product-time over kernel work; open weights keep the later self-host move open.

## Relationships

- Refines [SGLang and vLLM Comparison](sglang-vs-vllm.md) — adds benchmark-validity rules, workload-signal triage, and self-host economics to the workload-oriented comparison.
- Uses [SGLang Unified Radix Cache](sglang-unified-radix-cache.md) and [vLLM Prefix Caching](vllm-prefix-caching.md) — cache designs behind the prefix-reuse signal and TTFT probe.
- Uses [SGLang Structured Outputs](sglang-structured-outputs.md) and [vLLM Structured Outputs](vllm-structured-outputs.md) — backend context for the structured-output-share signal.
- Uses [Distributed Inference Core Concepts and Scaling Dimensions](distributed-inference-core-concepts.md) — prefill/decode and KPI context for the batch-shape signal and aggregate-versus-single-stream distinction.
- Uses [Speculative Decoding Workload Fit and Tuning](speculative-decoding-practice-guide.md) — context for the modification-case claim on self-trained draft models.

## Coverage limits

- Single-vendor DeepInfra evidence; the vendor sells managed endpoints, so treat the hosted-versus-self-host framing as interested guidance and redo break-even math on current rates.
- Cited AI Multiple and RunPod figures are second-hand summaries inside the source, not inspected primary harnesses.
- Companion KPI, provider-benchmark, pricing, and open-versus-closed posts are linked but were not inspected beyond the claims cited above.
- Release and star snapshots are dated 2026-07-14 and will drift; feature-convergence claims are source-attributed, not independently verified.
- The TTFT probe script was read for method only and not executed; hosted-endpoint cache behavior is opaque and concurrency-sensitive.

[^deepinfra-vllm-sglang]: DeepInfra, vLLM vs SGLang: Performance, Features & Deployment Compared — `../raw/vllm-vs-sglang/index.md` (deepinfra.com), covering version-mismatched and unit-conflated benchmark critiques, PagedAttention versus RadixAttention origins with V1 and zero-overhead scheduler notes, 2026-07-14 release and star snapshots, four workload signals, streaming TTFT prefix-reuse probe with confounders, 8-GPU self-host versus per-token break-even arithmetic, self-host-win conditions, and engine selection guidance.
