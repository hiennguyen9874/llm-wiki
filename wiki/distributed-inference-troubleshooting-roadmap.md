---
type: Concept
title: Distributed Inference Troubleshooting and Scaling Roadmap
description: TTFT/TPOT troubleshooting recipes, observability signals, canary rollout discipline, and staged scaling roadmap for vLLM and llm-d on OpenShift AI.
tags: [vllm, llm-d, troubleshooting, observability, scaling]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T15:00:00Z }
sources:
  - id: redhat-blueprints
    resource: ../raw/deploying-distributed-ai-inference-blueprints-troubleshooting/index.md
    title: "Deploying distributed AI inference: Blueprints & troubleshooting"
---

When TTFT or TPOT regresses, diagnose from emitted metrics before changing configuration, then scale the vLLM plus llm-d stack one measured step at a time[^redhat-blueprints].

## Diagnostic workflow

1. **Observe the regression:** TTFT up, TPOT up, or throughput down[^redhat-blueprints].
2. **Read the fleet metrics:** vLLM Prometheus queue time, scheduling delay, prefill duration, decode duration, and KV-cache utilization, plus llm-d scheduler routing decisions and per-worker queue depths[^redhat-blueprints].
3. **Locate the bottleneck:** gateway/routing, prefill, decode, or KV transfer[^redhat-blueprints].
4. **Deep-inspect only if needed:** Nsight Systems for end-to-end multi-process CPU+GPU coordination, Nsight Compute for a single-kernel bottleneck[^redhat-blueprints].

## Symptom-based recipes

| Symptom | Likely cause | First action |
| --- | --- | --- |
| Sudden TPOT rise + climbing KV utilization | KV-cache fragmentation or aggressive preemption | Adjust preemption threshold; verify chunked prefill is enabled so long prompts do not starve short decodes |
| MoE throughput degraded, 1–2 experts queue-deep | Hot-expert imbalance | Enable enhanced parameter-driven load balancing (EPLB); consider expert replication if it persists |
| Disaggregated fleet stable TTFT but TPOT spikes with prompt arrival | NIXL queue depths rising, blocking decode during KV transfer | Verify RDMA driver health; check NIXL metadata server is not a single point of failure |
| Speculative decoding on, throughput flat or down | Draft-head acceptance decayed | Inspect per-request acceptance metrics; model or workload may have drifted from draft training data |

- **A. TPOT + KV pressure:** sudden TPOT increase paired with climbing KV utilization usually means fragmentation or over-eager preemption; adjust the preemption threshold and confirm chunked prefill is on[^redhat-blueprints].
- **B. MoE hotspot:** degraded throughput with high queue depths on one or two experts signals hot-expert imbalance; enable EPLB and consider replication[^redhat-blueprints].
- **C. Transfer stall:** stable TTFT with spiked TPOT during prompt arrival points to rising NIXL queue depths blocking decode workers during KV transfers; check RDMA health and metadata-server redundancy[^redhat-blueprints].
- **D. Draft decay:** active speculative decoding with unchanged or decreased throughput means acceptance decay; inspect per-request acceptance because the model or workload may have drifted from draft training data[^redhat-blueprints].

## Safe rollout discipline

- Roll out config changes with canary deployments and gate on both TTFT and TPOT[^redhat-blueprints].
- Never change two scheduler parameters at once; multi-variable changes hide which parameter caused the fluctuation[^redhat-blueprints].
- Prefer diagnosis before tuning[^redhat-blueprints].

## Staged scaling roadmap

Practical sequence for standing up vLLM and llm-d on OpenShift AI; every step connects to a baseline and adds one mechanism only when measurements show the simpler setup hit its limit[^redhat-blueprints].

1. **Start simple and baseline:** single node, single vLLM instance; choose model and parallelism layout, then baseline TTFT and TPOT on production traffic for at least a week as the foundation for later decisions[^redhat-blueprints].
2. **Add smart routing with llm-d:** when the fleet stops scaling linearly — signal is a second replica behind a load balancer yielding less than 1.8× single-node throughput — because round-robin routing leaves cache hits on the table[^redhat-blueprints].
3. **Disaggregate and layer speculative decoding:** disaggregate only when measured prefill/decode imbalance justifies the network hop; premature disaggregation costs more than it saves; layer speculative decoding once concurrency stabilizes, since gains are largest at low concurrency and shrink under saturated high concurrency[^redhat-blueprints].
4. **Transition to distributed AI-grid:** when the platform serves more than one model class to multiple tenants; cascading, SLO classes, shared cache fabrics, and GitOps-managed pools pay off at multi-tenant scale but are overhead for smaller setups[^redhat-blueprints].
5. **Evolve policies:** per Figure 3, introduce SLO classes, priorities, quotas, and preemption to protect premium traffic once multiple traffic classes with different SLOs share the grid[^redhat-blueprints].
6. **Use the AI-grid when needed:** per Figure 3, adopt full multi-model, multi-tenant pools and governance only when more than one model class serves more than one tenant at meaningful scale[^redhat-blueprints].

Growth principles: re-baseline after each change so the next decision rests on data, not expectations; start simple, measure honestly, and optimize for the specific workload rather than letting a catalog dictate the next step[^redhat-blueprints].

## Red Hat stack mapping

| Component | Role |
| --- | --- |
| Red Hat OpenShift | Kubernetes substrate |
| Red Hat OpenShift AI | Model registry, pipelines, monitoring, governance |
| Red Hat AI Inference Server | Hardened vLLM with pinned kernels and LLM Compressor quantization |
| KServe | Serving lifecycle |
| llm-d | Distributed layer for cache-aware routing, disaggregation, and KV-cache-aware scheduling |

Each blueprint rung maps to this stack so capabilities can be adopted stepwise without hand-assembly[^redhat-blueprints].

## Relationships

- Related to [Distributed Inference Deployment Blueprints](distributed-inference-blueprints.md) — this concept operates and stages adoption of those six traffic-matched topologies.
- Related to [Distributed Inference Optimization Levers](distributed-inference-optimization-levers.md) — Part 2 lever mechanics (disaggregation sizing, cache sharing, spec-decoding acceptance) behind the recipes above.
- Uses [vLLM Metrics and Observability](vllm-metrics.md) — Prometheus per-request/batch signals, queue/scheduling/prefill/decode breakdown, and KV-utilization triage used in the workflow above.
- Uses [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) — transfer-stall recipe's prefill-to-decode KV leg.
- Uses [vLLM Chunked Prefill](vllm-chunked-prefill.md) — TPOT/fragmentation first action guarding short decodes from long prefills.
- Uses [vLLM Expert Parallel Deployment](vllm-expert-parallel-deployment.md) — MoE hotspot EPLB and replication path.
- Uses [vLLM NIXL Connector Usage](vllm-nixl-connector-usage.md) — disaggregated-transfer RDMA/metadata health check behind recipe C.
- Uses [vLLM Per-Request Speculative Decoding Acceptance Metrics](vllm-per-request-spec-decode-metrics.md) — draft-decay inspection behind recipe D.
- Uses [vLLM Tensor and Pipeline Parallel Scaling](vllm-parallelism-scaling.md) — single-node baseline parallelism choice in roadmap step 1.

## Coverage limits

- Local Figures 2–3 were visually inspected; Figure 2's workflow and recipe panels match the text, while Figure 3 shows six roadmap stages but the article text details only stages 1–4 — stages 5–6 above summarize the figure's policy-evolution and AI-grid-adoption panels, not body prose[^redhat-blueprints].
- vLLM Prometheus docs, llm-d scheduler docs, Nsight Systems/Compute docs, and linked Red Hat / llm-d / KServe / LLM Compressor / vLLM context-parallel and disaggregated-prefill references were not inspected beyond this source's summary[^redhat-blueprints].

[^redhat-blueprints]: Deploying distributed AI inference: Blueprints & troubleshooting — `../raw/deploying-distributed-ai-inference-blueprints-troubleshooting/index.md`, covering TTFT/TPOT diagnostic workflow and four symptom recipes, canary discipline, 1–4 staged roadmap plus Figure 3 six-stage map, growth principles, and OpenShift AI stack table.
