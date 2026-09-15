---
type: Concept
title: Distributed Inference Core Concepts and Scaling Dimensions
description: Prefill/decode trade-offs, five KPIs, and five parallelism dimensions with Qwen layout guidance for distributed LLM serving.
tags: [vllm, distributed-inference, parallelism, prefill-decode, long-context]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T15:00:00Z }
sources:
  - id: redhat-core-concepts
    resource: ../raw/designing-distributed-ai-inference-core-concepts-and-scaling-dimensions/index.md
    title: "Designing distributed AI inference: Core concepts and scaling dimensions"
---

Part 1 of the Red Hat distributed-inference series establishes mental models before config: map business workload to KPIs, then to runtime layout and production controls, with prefill/decode tension and five parallelism dimensions setting baseline limits[^redhat-core-concepts].

## Decision framework

Workload is shaped by business behind it: how many requests arrive at once, how long prompts and contexts run, subject-matter domain, and how much reasoning each request demands[^redhat-core-concepts].

Short-listed KPIs are time to first token (TTFT), time per output token (TPOT, or inter-token latency), throughput in requests/sec and tokens/sec, GPU utilization, and KV-cache hit rate; these trade against each other constantly[^redhat-core-concepts].

Figure 1 maps four quadrants around a central decision framework[^redhat-core-concepts]:

- **1. Workload signature:** chat interactive, RAG retrieval-augmented, batch/offline inference, AI-grid multi-tenant, edge/sovereign — understand traffic shape and user expectations.
- **2. KPI priority:** TTFT, TPOT, throughput tokens/sec, cost efficiency $/M tokens, availability and latency SLOs — define what success looks like.
- **3. Runtime layout:** single pool prefill+decode, prefill/decode disaggregated, DP-heavy replicated, edge-local/hybrid, multi-cluster/multi-region — choose topology matching workload and hardware.
- **4. Production controls:** cache-aware routing, backpressure and admission, autoscaling and bin-packing, canary and safe rollouts, observability and SLO alerts — operate predictably at scale.

## Ecosystem context

Three developments since the earlier vLLM-choice post[^redhat-core-concepts]:

- **llm-d in CNCF Sandbox:** clearer open-governance path; easier to evaluate where vendor neutrality, community stewardship, and long-term ecosystem alignment matter.
- **KV-cache management as first-class design:** NIXL, LMCache, and Mooncake compete and converge around KV transfer, reuse, and offload; affects latency, network requirements, failure handling, observability, hardware affinity, and prefill/decode pool sizing.
- **Speculative decoding practical path:** EAGLE 3.1 from EAGLE team, vLLM team, and TorchSpec landed late May 2026 with materially better long-context acceptance length than EAGLE-3; more relevant for long-document workloads, while acceptance rate, memory overhead, batching behavior, and operational complexity still decide whether enabling pays.

Example anchors are Qwen3.5 and Qwen3.6 families in dense Qwen3.6-27B and MoE Qwen3.5-35B-A3B and Qwen3.5-397B-A17B variants, spanning latency-sensitive dense, cost-efficient mid MoE, and high-capability large MoE; Qwen3.5 native 262,000-token context motivates context parallelism as a fifth dimension[^redhat-core-concepts].

## Prefill and decode

LLM inference is two workloads pretending to be one[^redhat-core-concepts]:

- **Prefill** processes input prompt in parallel and populates KV cache; dense matrix operations, compute-bound, primary driver of TTFT especially for long prompts and RAG.
- **Decode** generates tokens sequentially attending over accumulated KV cache; memory-bandwidth-bound stressing HBM capacity and bandwidth, primary driver of TPOT.

Figure 2 confirms the split: prefill best for fast prompt ingestion and first-token responsiveness, decode best for stable per-token generation under concurrency[^redhat-core-concepts].

They interfere on shared GPUs: aggressive prefill batching uses compute efficiently but can occupy the worker long enough to delay queued decode steps, raising TPOT; prioritizing decode protects inter-token latency but leaves prefill under-batched, wasting compute and raising long-prompt cost[^redhat-core-concepts].

Architectural fork[^redhat-core-concepts]:

- Run prefill and decode together on homogeneous workers with scheduler arbitration — default for single-GPU vLLM, right for many small/medium fleets because it is simpler and avoids KV-transfer overhead.
- Split across heterogeneous pools routing each request through both — threshold is not model size or token count but measurable phase imbalance large enough that right-sizing each pool exceeds KV-cache move cost.

## Five parallelism dimensions

Modern serving spans tensor, pipeline, expert, data, and context parallelism; context splits further into prefill context parallel (PCP) and decode context parallel (DCP)[^redhat-core-concepts]. Figure 3 common combinations are TP+DP for dense, TP+EP for MoE, TP+CP for long-context, and PP when the model spans nodes[^redhat-core-concepts].

### Tensor parallelism

Splits each weight matrix across GPUs with per-layer all-reduce; latency-sensitive within node and communication-heavy across nodes, so NVLink/NVSwitch budget decides scaling before all-reduce dominates[^redhat-core-concepts].

For dense models: try quantized version first, then minimum TP fitting model with adequate KV headroom, then scale out with DP; stringent single-request TTFT SLO can justify higher TP[^redhat-core-concepts]. For MoE where DP ranks coordinate on expert layers, TP/DP split determines expert distribution[^redhat-core-concepts].

### Pipeline parallelism

Splits by layer ranges passing activations point-to-point at stage boundaries rather than per-layer all-reduce; far more tolerant of limited inter-node bandwidth and can run over Ethernet-class fabrics where cross-node TP stalls[^redhat-core-concepts].

Tolerance is relative: handoffs sit on critical path, activation volume grows with batch size, sequence length, and hidden dimension, and link latency widens bubbles when stages wait; micro-batching keeps stages fed[^redhat-core-concepts]. Last resort, not default: quantize first, then try EP+DP on one node, reach for PP only when weights genuinely do not fit[^redhat-core-concepts].

### Expert parallelism

Distributes MoE experts across GPUs; each token routes only to assigned subset so traffic is asymmetric and bursty, and one or two popular experts can anchor tail latency under skewed routing[^redhat-core-concepts].

Expert Parallel Load Balancing can replicate hot experts and rebalance dynamically but is not free — under stable routing rebalancing overhead can exceed benefit, so enable when monitoring confirms persistent imbalance rather than as blanket default[^redhat-core-concepts]. Further costs: couples otherwise-independent DP ranks because expert layers synchronize every forward pass, and requires all-to-all traffic scaling with active experts and batch size[^redhat-core-concepts].

### Data parallelism

Runs full replicas behind load balancer for linear throughput scaling with no sharding complexity; common start when model fits one node and bottleneck is concurrency; KServe ReplicaSet handles this case[^redhat-core-concepts]. DP alone does not set ceiling — parallelism config and routing set real limit[^redhat-core-concepts].

Common pitfalls: stacking replicas without checking API-server bottlenecks, ignoring KV hit rate and MoE synchronization overhead, and underestimating multi-node network costs[^redhat-core-concepts].

### Context parallelism

Shards sequence dimension so one request's context need not fit or compute on one device; applied separately as PCP and DCP because phases carry different SLOs[^redhat-core-concepts].

**Prefill context parallel targets TTFT:** attention cost grows quadratically with prompt length; PCP partitions sequence across devices computing attention chunks in parallel, splitting prefill compute and lowering TTFT at hardware cost of TP × PCP devices in its own communication domain; reach for it when prefill compute dominates TTFT and GPU budget allows[^redhat-core-concepts].

**Decode context parallel targets throughput:** bottleneck is KV capacity — more KV tokens held means larger batch and higher throughput; DCP shards KV along sequence across GPUs already in TP group, reusing TP domain with no extra devices[^redhat-core-concepts].

Most valuable for few-KV-head models such as Qwen3.5: under plain TP with fewer KV heads than TP ranks, KV replicates across ranks wasting HBM, and DCP removes duplication handing memory back to batch; supported in vLLM for MLA and GQA, with some backends combining DCP and multi-token prediction[^redhat-core-concepts].

Rule: DCP costs no extra GPUs and directly reduces duplication, so reach for it first; add resource-intensive PCP when long prefill exceeds TTFT budget[^redhat-core-concepts].

## Suggested Qwen layouts

vLLM computes EP = TP × DP per pipeline stage, so EP values below are convenience labels; optimal mix depends on architecture and hardware, with EP latency-optimal for limited-KV-head models like Qwen3 while DP maximizes throughput but can add dispatch-bubble latency during prefill/decode[^redhat-core-concepts].

| Model | Hardware/precision | Suggested layout | Notes |
| --- | --- | --- | --- |
| Qwen3.6-27B dense | 1×H100 FP8 | `TP=1` | ~27 GB weights; single-GPU baseline |
| Qwen3.6-27B dense | 8×H100 FP8 | `DP=8` | `TP=1` per replica |
| Qwen3.5-35B-A3B MoE | 8×H100 FP8 | `DP=8`, `--enable-expert-parallel` | `EP=8`; experts sharded |
| Qwen3.5-35B-A3B MoE | 8×H100 BF16 | `TP=2`, `DP=4`, `--enable-expert-parallel` | ~70 GB weights → `TP=2` to fit; `EP=8` |
| Qwen3.5-397B-A17B MoE | 16×H100 2 nodes FP8 | `PP=2`, `EP=8`, `--enable-expert-parallel` | ~397 GB weights; layers split across nodes, experts within each |
| Any Qwen3.5 ≥128k decode | + DCP | `--decode-context-parallel-size 2` | Shards KV on existing TP GPUs; no new devices |
| Any Qwen3.5 ≥128k prefill | + PCP | `--prefill-context-parallel-size 2` | Adds GPUs as `TP × PCP` |

## Relationships

- Uses [vLLM Tensor and Pipeline Parallel Scaling](vllm-parallelism-scaling.md) — single-replica TP/PP selection, runtimes, and networking behind the TP and PP guidance above.
- Uses [vLLM Data Parallel Deployment](vllm-data-parallel-deployment.md) — replica scaling, load-balancing modes, and MoE DP+EP coordination behind the DP guidance above.
- Uses [vLLM Expert Parallel Deployment](vllm-expert-parallel-deployment.md) — EP sharding, all-to-all backends, and EPLB mechanics behind the EP guidance above.
- Uses [vLLM Context Parallel Deployment](vllm-context-parallel-deployment.md) — PCP/DCP strategies, KV-sharding mechanics, and sizing behind the CP guidance above.
- Uses [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) — homogeneous versus heterogeneous prefill/decode fork and KV-transfer cost threshold.
- Uses [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — EAGLE 3.1 long-context optimization path mentioned in ecosystem updates.
- Related to [Distributed Inference Deployment Blueprints](distributed-inference-blueprints.md) — Part 3 blueprints instantiate this Part 1 framework for six traffic shapes.
- Related to [Distributed Inference Optimization Levers](distributed-inference-optimization-levers.md) — Part 2 disaggregation, KV-cache, and speculative-decoding levers that optimize past this baseline.
- Related to [Distributed Inference Troubleshooting and Scaling Roadmap](distributed-inference-troubleshooting-roadmap.md) — operational companion for TTFT/TPOT triage once this layout is deployed.
- Related to [Qwen3.6 Local Deployment](qwen3.6.md) — local-build view of the Qwen3.6-27B dense anchor referenced in layout table.

## Coverage limits

- All three local figures were visually inspected; Figure 1 quadrant labels, Figure 2 phase/interference panels, and Figure 3 per-dimension plus common-combination rows are reflected above[^redhat-core-concepts].
- Part 2 advanced deployment patterns, the earlier vLLM-choice post, Telco-AIX assessments, llm-d CNCF status, NIXL/LMCache/Mooncake designs, TorchSpec/EAGLE 3.1 results, and Qwen3.5/Qwen3.6 model cards were linked but not compiled here; model sizes, 262k context, layout table, and EAGLE claims are source-reported[^redhat-core-concepts].
- Qwen weight footprints and H100 fit guidance are source-reported and not independently verified; cross-check precision, KV headroom, and accelerator memory before sizing[^redhat-core-concepts].
- Source last updated July 7, 2026; vLLM flags and parallelism defaults may have evolved since[^redhat-core-concepts].

[^redhat-core-concepts]: Designing distributed AI inference: Core concepts and scaling dimensions — `../raw/designing-distributed-ai-inference-core-concepts-and-scaling-dimensions/index.md`, covering decision framework, five KPIs, prefill/decode split and disaggregation threshold, 5D TP/PP/EP/DP/PCP/DCP guidance, Qwen3.5/Qwen3.6 layout table, and ecosystem updates on llm-d, KV-cache projects, and EAGLE 3.1.
