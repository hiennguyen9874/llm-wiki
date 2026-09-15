---
type: Concept
title: Distributed Inference Optimization Levers
description: Prefill/decode disaggregation decision and sizing, tiered and shared KV-cache architecture, and speculative-decoding selection with production failure modes.
tags: [vllm, llm-d, distributed-inference, kv-cache, speculative-decoding]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: redhat-opt-levers
    resource: ../raw/optimizing-distributed-ai-inference-advanced-deployment-patterns/index.md
    title: "Optimizing distributed AI inference: Advanced deployment patterns"
---

Part 2 of the Red Hat distributed-inference series moves past parallelism layout into three optimization levers — prefill/decode disaggregation, KV-cache architecture, and speculative decoding — each trading operational complexity for cost, latency, or throughput gains once the baseline is set[^redhat-opt-levers].

## Prefill/decode disaggregation as topology

Disaggregation is treated here as a deployment topology, not a checkbox feature: separate prefill and decode pools joined by a KV-transfer fabric, fronted by Envoy AI Gateway and the llm-d scheduler[^redhat-opt-levers].

### Decision rule

Profile a single-pool baseline on real traffic and compare two ratios[^redhat-opt-levers]:

- measured prefill GPU-seconds versus decode GPU-seconds;
- cost of decode-optimized versus prefill-optimized GPUs in your environment.

The gap between those ratios is the available savings. Disaggregation pays for long-prompt RAG with short answers (prefill-heavy), high-concurrency chat with short prompts and long answers (decode-heavy), or any fleet large enough that savings exceed complexity[^redhat-opt-levers].

Source-reported evidence is illustrative, not a guarantee: 25–40% cost reduction on chat- and RAG-shaped traffic in the authors' benchmarks, versus Splitwise at ~20% lower cost and 1.4× throughput and DistServe at up to 7.4× higher goodput in published results[^redhat-opt-levers].

It does not pay for single-node deployments where the prefill-to-decode network hop exceeds savings, or for fleets so small that two pools of one worker lose to one pool of two workers[^redhat-opt-levers].

### Sizing the two pools

Prefill scales with new-prompt arrival rate and prompt-length distribution; decode scales with concurrent sessions, mean output length, and TPOT target, independently[^redhat-opt-levers].

First-cut lab numbers for chat (mean 800-token prompt, 200-token output, 5,000 concurrent sessions on Qwen3.5-35B-A3B): roughly one H100 of prefill per ~30 req/s arrival, and roughly one decode GPU per ~150 concurrent sessions, for a broadly stable 1:3 to 1:5 prefill-to-decode worker ratio across benchmarked chat workloads — all source-reported and model/quantization dependent[^redhat-opt-levers].

### KV-transfer connectors and data path

vLLM exposes a KVConnector interface; four production-relevant options are compared[^redhat-opt-levers]:

| Connector | Recommended for | Transport | Notes |
| --- | --- | --- | --- |
| `NixlConnector` | Single-cluster with RDMA/NVLink | NVIDIA NIXL over UCX | Default for high-performance PD; metadata server is a startup SPOF |
| `LMCacheConnector` | Cross-instance sharing, HBM → DRAM → NVMe tiering | NIXL plus offload backends | Adds tiered cache plus shared prefix index |
| `MooncakeConnector` | Cluster-scale shared cache pools | RDMA-native | Separate KV-cache cluster many instances pull from |
| `MooncakeStoreConnector` | Tiered offload via distributed master store | Cache offloading | Offload tier behind `MooncakeConnector`; KV lands in master store, not peer HBM |

Treat the fabric as a production data path: measure end-to-end latency including queue time, alert on tail latency not the mean, verify RDMA driver health per node, and use NIXL async send/recv so prefill never blocks on decode acknowledgement[^redhat-opt-levers].

### Cluster-wide KV pool and cache-aware routing

Instead of per-worker memory plus a transfer protocol, view KV cache as a cluster resource: LMCache tiers across HBM, DRAM, and NVMe with a global prefix index so requests sharing a system prompt, few-shot prefix, or long-document head share blocks regardless of originating instance[^redhat-opt-levers].

llm-d turns this into a deployment pattern by routing each request to the worker holding its warmest KV state rather than round-robin[^redhat-opt-levers]. Published llm-d benchmarks claim up to 57× faster TTFT and 2× throughput under high prefix reuse (8 pods, 16 H100s); the authors' own lab figures are 25% on defaults, 2–3× tokens/s/GPU with prefix-hit routing, and 3–5× cost/token reduction on high-reuse chat — presented as illustration with production variance expected[^redhat-opt-levers].

### Emerging: hybrid GPU-CPU prefill

CPUs handle early prefill (embedding lookups, attention prep) while GPUs take matrix multiplies. Not a primary production recommendation yet, but a separately scheduled prefill pool lets worker type change as hardware matures without re-architecting[^redhat-opt-levers].

### Failure modes

- NIXL metadata server is a startup SPOF: run two behind a TCP load balancer and verify failover before the first canary[^redhat-opt-levers].
- Lagging decode workers during KV transfer anchor fleet tail latency: prefer gateway admission control over downstream retries[^redhat-opt-levers].
- Canary only one pool at a time, with automated rollback gates on both TTFT and TPOT[^redhat-opt-levers].

## KV cache: tiering, sharing, squeezing

PagedAttention solved single-GPU fragmentation; distributed pressure moves to cross-GPU and cluster scope[^redhat-opt-levers].

### Tiered hierarchy

Enable tiering when inactive prefixes fit in DRAM/NVMe but exceed HBM: if a 10× larger-than-HBM cache raises prefix-hit rate, tiering pays[^redhat-opt-levers].

### Prefix sharing versus KV reuse

Distinct concerns requiring different config[^redhat-opt-levers]:

- **Prefix sharing:** two requests starting with the same tokens share one cache entry; a routing function sending the new request to the worker with the warm prefix; serves shared system prompts.
- **KV reuse:** one request's data retained across turns of a live session; a session-affinity function pinning the conversation to the same decode worker; serves conversation history.

Multi-tenant chat needs both[^redhat-opt-levers].

### Quantization

FP8 KV halves memory with usually acceptable quality cost on enterprise tasks; FP4 is aggressive and should only deploy after an eval pass on your own data[^redhat-opt-levers]. Red Hat's LLM Compressor produces quantized Qwen variants validated against your eval set rather than a generic benchmark[^redhat-opt-levers].

### Decode kernels and supply chain

2026 decode speed comes from combined advances including DeepSeek FlashMLA, Stanford ThunderMLA, and PyTorch FlexAttention decode paths[^redhat-opt-levers]. Platform teams rarely tune kernels directly, but knowing the build's kernel explains post-upgrade regressions[^redhat-opt-levers].

Every prefill, decode, and draft replica must load identical pinned kernel binaries: compile from source into the container with an SBOM rather than pulling on first request; the source points to a GPU-kernel companion post and GPU Kernel Manager bridge for heterogeneous-fleet trade-offs[^redhat-opt-levers].

### PagedAttention versus RadixAttention

SGLang RadixAttention organizes cache as a prefix tree so conversation structure guides eviction; PagedAttention treats cache like virtual-memory pages[^redhat-opt-levers].

Source guidance: RadixAttention excels on deep branching prefix trees (agent workflows, structured prompting); PagedAttention fits irregular prefixes and varied sequence lengths[^redhat-opt-levers]. vLLM stays with PagedAttention as a general-purpose runtime whose page abstraction moves naturally across disaggregated architectures[^redhat-opt-levers].

## Speculative decoding

Draft path proposes multiple candidates cheaply; the target verifies them, emitting several tokens per forward pass on acceptance[^redhat-opt-levers].

- **Two-model draft-based (EAGLE family):** small draft proposes, target verifies; EAGLE-3 reported up to 6× on dense models, EAGLE 3.1 up to 2× the acceptance length of EAGLE-3 on long context and a starting choice for dense Qwen3.6[^redhat-opt-levers].
- **Single-model self-speculative:** subset of own layers drafts and full model verifies; no separate draft to train or host, but acceptance varies with workload[^redhat-opt-levers].
- **Multi-token decoding (Medusa heads):** extra output heads predict several tokens per pass at roughly half the engineering cost of EAGLE-3 with modest 0.55–0.70 acceptance[^redhat-opt-levers].
- **Interleaved decode:** scheduling choice mixing spec-decoded and normal sessions to keep batches full, not a separate technique[^redhat-opt-levers].
- **Multi-token prediction (MTP):** models shipping jointly trained MTP heads (e.g. DeepSeek-V3) can exceed 80% acceptance out of the box; cannot be retrofitted without retraining[^redhat-opt-levers].

Workload selection from the source[^redhat-opt-levers]:

| Workload | Anchor | Recommended | Why |
| --- | --- | --- | --- |
| Short conversational, dense | Qwen3.6-27B | EAGLE 3.1 | Best accept-rate/cost ratio, current generation |
| Long-context (>64k) | Qwen3.5 dense or MoE | EAGLE 3.1 | Long-context acceptance headline |
| MoE flagship | Qwen3.5-397B-A17B | Native MTP if trained, else EAGLE-3 | Active-param shape favors MTP-style heads |
| Code completion | Qwen3.6 dense | n-gram / prompt-lookup | Repetitive structure, high hit rate, no draft to host |
| Strict memory budget | any | n-gram | No draft on decode HBM |
| Heavy tool-calling | any | Disable or test | Constrained-decoding interaction is severe |

Saturation caveat: the draft occupies decode HBM and adds verification overhead, so gains shrink on already-saturated large-batch fleets and can go net-negative; clearest wins are at low-to-moderate concurrency with underutilized forward passes[^redhat-opt-levers].

## Putting the levers together

Disaggregation, cache architecture, and speculative decoding are individual mechanisms; the deployment question is how they combine for a traffic shape and what to do on regression — covered in the series' blueprints and troubleshooting companion[^redhat-opt-levers].

## Relationships

- Related to [Distributed Inference Core Concepts and Scaling Dimensions](distributed-inference-core-concepts.md) — Part 1 prefill/decode split and five parallelism dimensions this Part 2 optimizes past.
- Related to [Distributed Inference Deployment Blueprints](distributed-inference-blueprints.md) — Part 3 blueprints that combine these three levers per traffic shape.
- Related to [Distributed Inference Troubleshooting and Scaling Roadmap](distributed-inference-troubleshooting-roadmap.md) — operational companion for TTFT/TPOT regression on these levers.
- Uses [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) — connector-mediated prefill/decode split and no-throughput caveat behind the topology decision above.
- Uses [vLLM NIXL Connector Usage](vllm-nixl-connector-usage.md) — NixlConnector transport, deployment, and health checks behind the data-path guidance.
- Uses [vLLM Mooncake Connector](vllm-mooncake-connector.md) — RDMA shared-pool transfer behind the Mooncake row.
- Uses [vLLM Mooncake Store Connector](vllm-mooncake-store-connector.md) — distributed-master offload tier behind the MooncakeStore row.
- Uses [vLLM Prefix Caching](vllm-prefix-caching.md) — block-reuse mechanics behind prefix sharing; this concept adds the routing versus session-affinity split.
- Uses [vLLM Quantized KV Cache](vllm-quantized-kv-cache.md) — FP8/FP4 formats and backend constraints behind the squeezing guidance.
- Uses [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — EAGLE/Eagle3 draft-target mechanism behind the two-model recommendation.
- Uses [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — native MTP path for models shipping trained heads.
- Uses [vLLM Draft-Model Speculative Decoding](vllm-draft-model.md) — generic draft-target verification framing.
- Uses [vLLM N-Gram Speculative Decoding](vllm-ngram-speculative-decoding.md) — draft-free path recommended for code and memory-constrained rows.
- Related to [Speculative Decoding Workload Fit and Tuning](speculative-decoding-practice-guide.md) — acceptance-rate and draft-token tuning complementing the method-selection table; see Contradictions on constrained decoding.
- Related to [vLLM Chunked Prefill](vllm-chunked-prefill.md) — prefill/decode interference control alternative to full disaggregation.
- Related to [SGLang PD Disaggregation](sglang-pd-disaggregation.md) — SGLang-side disaggregation counterpart to this vLLM/llm-d topology.

## Contradictions

- Constrained/structured output fit is unresolved: this source warns speculative acceptance often collapses under constrained decoding (JSON mode, grammar tool calls) because the mask invalidates drafts and advises measuring before assuming benefit[^redhat-opt-levers]; the companion [Speculative Decoding Workload Fit and Tuning](speculative-decoding-practice-guide.md) lists structured outputs (JSON, XML, SQL) as strong fits. Treat tool-calling and grammar-constrained traffic as measure-first rather than default-on.

## Coverage limits

- All three local figures were visually inspected: Figure 1 gateway → scheduler → prefill pool → KV fabric → decode pool flow, Figure 2 tiered HBM/DRAM/NVMe plus prefix-sharing versus session-affinity split, and Figure 3 four-method spec-decoding map with pay-off/caution footer are reflected above[^redhat-opt-levers].
- Splitwise, DistServe, LMCache (arXiv:2510.09665), PagedAttention, RadixAttention, FlashMLA, ThunderMLA, EAGLE-3/EAGLE 3.1, Medusa, DeepSeek-V3, llm-d v0.5 benchmarks, Envoy AI Gateway write-up, GPU-kernel companion, and vLLM FP8-KV-cache post were linked but not compiled here; all benchmark, sizing, acceptance, and cost figures are source-reported lab measurements, not independently verified[^redhat-opt-levers].
- Qwen3.5-35B-A3B, Qwen3.6-27B, and Qwen3.5-397B-A17B sizing and fit claims are source-reported; cross-check precision, KV headroom, and accelerator memory before sizing[^redhat-opt-levers].
- Source last updated July 7, 2026; vLLM connector names, flags, and kernel defaults may have evolved since[^redhat-opt-levers].

[^redhat-opt-levers]: Fatih E. Nar, Optimizing distributed AI inference: Advanced deployment patterns — `../raw/optimizing-distributed-ai-inference-advanced-deployment-patterns/index.md` (Red Hat Developer, 2026-06-24), covering P/D disaggregation decision/sizing/connectors/llm-d routing/failure modes, KV tiering/sharing/quantization/kernels/Paged-versus-Radix, four speculative-decoding methods plus interleaved scheduling with workload table and saturation caveat, and pointer to blueprints/troubleshooting sequel.
