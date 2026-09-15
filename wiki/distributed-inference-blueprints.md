---
type: Concept
title: Distributed Inference Deployment Blueprints
description: Six vLLM and llm-d deployment blueprints matched to traffic shapes from high-concurrency chat to edge inference with topology, mechanisms, and cost shapes.
tags: [vllm, llm-d, deployment, inference-serving, topology]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T15:00:00Z }
sources:
  - id: redhat-blueprints
    resource: ../raw/deploying-distributed-ai-inference-blueprints-troubleshooting/index.md
    title: "Deploying distributed AI inference: Blueprints & troubleshooting"
---

Part 3 of the Red Hat distributed-inference series assembles prefill/decode, parallelism, disaggregation, KV-cache, and speculative-decoding tools into six deployment blueprints matched to traffic shape[^redhat-blueprints]. Each blueprint uses the same structure — workload signature, KPI priority, topology, vLLM and llm-d mechanisms, cost shape — and is a flexible starting point, not a rigid prescription[^redhat-blueprints].

| Traffic shape | KPI priority | Topology gist | Cost shape |
| --- | --- | --- | --- |
| High-concurrency chat / copilots | TPOT-sensitive | Disaggregated prefill + decode, cache-aware routing, EAGLE 3.1, LMCache tiering | Decode-dominated |
| Long-context RAG / code | TTFT-sensitive | TP + prefill context parallel, small decode pool, prefix caching | Prefill-dominated |
| High-throughput batch | Throughput / $ | Data-parallel replicas, max batching, aggressive quant | $/token utilization |
| Distributed AI-grid MaaS | Multi-tenant SLOs | Per-model InferencePools, gateway, cascading, admission control, shared cache | Non-linear utilization |
| Hybrid sovereign + cloud-burst | Compliance + elasticity | Single control plane, gateway across on-prem + burst, fast warm-up | CapEx baseline + spike OpEx |
| Edge workstation GPU | Local responsiveness | Single vLLM per accelerator, no disaggregation | CapEx-dominated |

## High-concurrency chat and copilots

- **Signature:** thousands of concurrent users, short prompts and outputs averaging a few hundred tokens, frequent reuse of system prompts and few-shot exemplars; keep TPOT within SLOs[^redhat-blueprints].
- **Topology:** disaggregated prefill and decode; large prefill pool on cost-optimized GPUs such as H100s with more HBM-capable H200/B200-class systems for decode, especially long-context[^redhat-blueprints].
- **Mechanisms:** cache-aware routing via llm-d scheduler pins each session to the decode worker holding its warm KV cache; EAGLE 3.1 runs on decode workers; LMCache offloads HBM to pinned DRAM and to NVMe for longest-tail conversations, making effective decode cache several times HBM[^redhat-blueprints].
- **Prefill protection:** chunked prefill prevents a long prompt from blocking short ones queued behind it; front-door prompt compression, debouncing and request coalescing for chatty UIs, and output token caps guard against runaway generation[^redhat-blueprints].
- **Cost:** decode-dominated; right-sizing the decode pool yields the greatest $/Mtoken savings[^redhat-blueprints].

## Long-context RAG and code analysis

- **Signature:** lower concurrency than chat, prompts 32,000–256,000 tokens, outputs in the hundreds, SLOs dominated by TTFT[^redhat-blueprints].
- **Topology:** tensor parallelism within the node plus prefill context parallel across GPUs so O(n²) attention is split rather than exhausting HBM on one device; decode pool stays small because prompt length binds more than concurrency[^redhat-blueprints].
- **TTFT levers:** prefill context parallel execution plus prefix caching; chunked prefill is explicitly not a TTFT reducer here — enabled by default in vLLM v1, it prevents a long prefill from starving other requests' decode steps at a little overhead on long prompts, while prefix caching is the primary saver[^redhat-blueprints].
- **Reuse:** warm prefix lives in a shared cache pool any decode worker can reach, so the second pass over a document never requires re-prefill[^redhat-blueprints].
- **Cost:** prefill-dominated; prefix-cache hit rate drives $/Mtoken because avoiding long-document re-prefill is direct savings[^redhat-blueprints].

## High-throughput batch

- **Signature:** latency-tolerant summarization, labeling, and embedding pipelines, throughput- and budget-bound, often overnight on backlogs[^redhat-blueprints].
- **Topology:** data parallelism with as many replicas as budget allows, each running continuous batching at maximum capacity; prefill-decode disaggregation provides no benefit because per-request time does not matter and the transfer hop is unnecessary[^redhat-blueprints].
- **Scheduling and efficiency:** continuous scheduling reorders requests to keep batches full under bursty arrival, distinct from continuous batching; dynamic quantization can be tuned more aggressively than interactive because small quality loss beats GPU expansion; scale to zero between waves via KServe with KEDA; spot or preemptible instances fit because batch retry is cheap[^redhat-blueprints].
- **Cost:** strictly $/token; maximum batching, aggressive quantization, scale-to-zero, and spot capacity directly minimize $/Mtokens[^redhat-blueprints].

## Distributed AI-grid Model-as-a-Service

- **Signature:** most architecturally diverse; platform team serves multiple tenants and models — e.g. Qwen3.6-27B for one product, Qwen3.5-35B-A3B for another, Qwen3.5-397B-A17B reserved for hard queries — across varied SLOs and bursty traffic as a grid, not single-purpose pools[^redhat-blueprints].
- **Topology:** each model class behind its own llm-d InferencePool with KServe LLMInferenceService resources in GitOps; AI-gateway implementations such as Envoy AI Gateway handle tenant authentication, rate limiting, and request classification; shared LMCache fabric reuses system-prompt prefixes across same-model instances; KEDA autoscaling runs per request class so gold-tier bursts scale fast while bronze scales gradually[^redhat-blueprints].
- **Model cascading:** route simple queries to the smallest capable model and escalate only on low-cost confidence signal or tenant policy, e.g. Qwen3.6-27B → Qwen3.5-35B-A3B → Qwen3.5-397B-A17B; cited as 40–60% cluster-cost reduction where basic queries dominate; operates in the gateway, not inside an InferencePool, so routing changes without redeploying models[^redhat-blueprints].
- **SLO-aware admission control:** healthier than queuing requests that will miss deadlines because long queues create tail-latency anchors; gateway admits gold ahead of silver ahead of bronze and rejects likely token-limit or timeout requests at the gateway with a specific error code before they burn GPU cycles[^redhat-blueprints].
- **Adaptive scheduling and hotspot prevention:** balances llm-d routing with cluster-level allocation; listed as early engineering/research: adaptive parallelism switching TP/PP with traffic, dynamic FP8/FP4 precision under load, continuous CUDA-graph prewarming from time-series prediction, and MoE expert rebalancing; requires per-tenant SLO classes and telemetry-driven config from the start so static variables can later become adaptive without re-architecture[^redhat-blueprints].
- **Cost:** most non-linear; well done it supports many tenants at high utilization, poorly done it fragments into low-utilization single-tenant pools; outcome depends on cascading, admission control, and shared-cache design[^redhat-blueprints].

## Hybrid sovereign to cloud-burst

- **Signature:** regulated baseline must run on-premises for residency, sovereignty, or contract reasons, bursting to public cloud only when spikes exceed on-premises capacity without violating compliance[^redhat-blueprints].
- **Topology:** Red Hat OpenShift AI on OpenShift as single control plane across environments; shared-registry model artifacts with GitOps drift control; llm-d inference gateway fronts both clusters with congestion-aware and topology-aware scheduling to the cluster with capacity and a warm prefix[^redhat-blueprints].
- **Burst readiness:** burst cluster stays idle most of the time; fast deterministic warm-up with pre-pulled pinned images and kernels keeps a minimal footprint, plus optional predictive prewarming from time-series forecasting so CUDA graphs and KV pools are warm before traffic shifts[^redhat-blueprints].
- **Cost:** CapEx-anchored on-premises baseline plus variable cloud OpEx paid only during spikes; works only if burst stays fully idle between peaks, so fast warm-up — not standing capacity — drives efficiency[^redhat-blueprints].

## Edge inference on workstation-class GPU

- **Signature:** single physical site — factory, store, clinic, branch, vehicle, or regional closet — where residency, latency, or connectivity blocks cloud use and backhaul is expensive or unreliable; typically 1–50 concurrent users where TTFT and TPOT both matter but volume fits one accelerator[^redhat-blueprints].
- **Topology:** single vLLM instance per accelerator with no llm-d disaggregation because the prefill-decode transfer hop costs more than it saves below ~100 concurrent sessions; KServe manages lifecycle; single-node OpenShift for single sites or multi-node OpenShift for regional handful-card installs; GitOps pins the same model build fleet-wide, e.g. same Qwen3.6-27B everywhere[^redhat-blueprints].
- **Why Qwen3.6-27B fits 96 GB:** hybrid architecture uses Gated DeltaNet linear attention in three of four attention sublayers, so only 16 of 64 layers keep per-token KV cache; with 4 KV heads at head_dim 256, per-token KV is ~64 KB in FP16 or ~32 KB in FP8, far below a pure transformer of similar size[^redhat-blueprints].
- **Capacity math:** after ~27 GB FP8 weights plus ~4 GB working memory, ~65 GB remains for ~2M tokens cumulative FP8 KV cache — about 50 sessions at 32K, 15 at 128K, or 4 at 512K using FP4 KV; Qwen3.5-35B-A3B at FP8 leaves ~55 GB for moderate concurrency, while Qwen3.5-397B-A17B cannot fit one card at any production precision because the full expert table must stay resident[^redhat-blueprints].
- **Hardware as substrate:** workstation cards such as RTX PRO 6000 96 GB Blackwell, deskside superchips such as DGX Spark, and Supermicro Super AI Station differ in bandwidth and capacity but share one software recipe — quantize to fit one accelerator, serve one vLLM instance, scale with data-parallel replicas before sharding; without NVLink-class links between enclosures, multi-box expansion uses pipeline or expert sharding for capacity rather than tensor parallelism for throughput[^redhat-blueprints].
- **Decode economics:** decode is memory-bandwidth limited and CapEx-dominated, so $/MToken stays unclear until a site passes ~100 concurrent sessions and resembles a regional cluster[^redhat-blueprints].
- **Multi-tier pattern:** route occasional over-difficult queries over backhaul to a regional AI-grid; local-gateway model cascading keeps the fastest path on-device and escalates only on confidence signal or policy, preserving local p99 while bounding backhaul because escalations are a small fraction[^redhat-blueprints].

## Relationships

- Uses [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) — chat blueprint's prefill/decode split and transfer hop; long-context and batch sections constrain when the hop pays.
- Uses [vLLM Context Parallel Deployment](vllm-context-parallel-deployment.md) — long-context RAG prefill context parallel strategy for O(n²) attention sharding.
- Uses [vLLM Data Parallel Deployment](vllm-data-parallel-deployment.md) — batch blueprint's replica scaling and edge scale-out-before-shard rule.
- Uses [vLLM Prefix Caching](vllm-prefix-caching.md) — long-context primary TTFT saver and AI-grid shared-cache reuse mechanism.
- Uses [vLLM Chunked Prefill](vllm-chunked-prefill.md) — chat stall-free scheduling and long-context starvation guard, with long-prompt overhead caveat.
- Uses [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — chat decode-worker EAGLE 3.1 acceleration.
- Uses [Qwen3.6 Local Deployment](qwen3.6.md) — edge blueprint's reference Qwen3.6-27B build and AI-grid model-cascade member.
- Related to [Distributed Inference Optimization Levers](distributed-inference-optimization-levers.md) — Part 2 decision rules, sizing, connectors, cache, and spec-decoding selection behind these topologies.
- Related to [Distributed Inference Troubleshooting and Scaling Roadmap](distributed-inference-troubleshooting-roadmap.md) — operational companion covering TTFT/TPOT triage and staged adoption of these blueprints.

## Coverage limits

- All three local figures were visually inspected and Reflected above; Figure 1's six-panel blueprint map adds no topology beyond the text except per-panel priority/cost labels preserved in the overview table[^redhat-blueprints].
- Parts 1–2 of the series, Envoy AI Gateway write-up, kernel/supply-chain companion, vLLM context-parallel and disaggregated-prefill docs, llm-d/KServe/KEDA product docs, and the model-cascade arXiv paper were linked but not compiled here; cascade 40–60% savings and Qwen model-family examples are source-reported claims[^redhat-blueprints].
- Qwen3.6-27B KV math, FP8/FP4 capacity profiles, and workstation-hardware fit claims are source-reported and not independently verified; cross-check accelerator memory and model build before sizing[^redhat-blueprints].

[^redhat-blueprints]: Deploying distributed AI inference: Blueprints & troubleshooting — `../raw/deploying-distributed-ai-inference-blueprints-troubleshooting/index.md`, covering six traffic-matched blueprints with signature, KPI, topology, vLLM/llm-d mechanisms, and cost shape, including Qwen3.6/Qwen3.5 cascade and edge capacity examples.
