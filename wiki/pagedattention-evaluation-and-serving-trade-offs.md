---
type: Concept
title: PagedAttention evaluation and serving trade-offs
description: In the SOSP 2023 evaluation, vLLM's paged KV management improved author-measured throughput and sharing efficiency, subject to custom baselines, workload, hardware, and block-size constraints.
tags: [pagedattention, vllm, kv-cache, llm-serving, evaluation, throughput]
status: stable
created: 2026-08-10
generated: { by: llm-wiki-agent/1, at: 2026-08-10T14:50:04Z }
sources:
  - id: pagedattention-2023
    resource: ../raw/arXiv-2309.06180v1/main.tex
    title: "Efficient Memory Management for Large Language Model Serving with PagedAttention"
---

# PagedAttention evaluation and serving trade-offs

Kwon et al.'s SOSP 2023 experiments report that vLLM's PagedAttention-based cache management sustains higher request rates at comparable normalized latency than FasterTransformer and the paper's author-implemented Orca variants. The results support the paper's design under its A100, OPT/LLaMA, and synthetic-trace configurations; they are not a general performance guarantee for current systems.[^pagedattention-2023]

## Evaluated outcomes

For the paper's basic-sampling workloads, vLLM sustained $1.7$–$2.7\times$ higher request rates than Orca (Oracle) and $2.7$–$8\times$ higher than Orca (Max) on ShareGPT traces at similar latency; it sustained up to $22\times$ FasterTransformer's request rate. The paper attributes the advantage to fitting more active requests into cache, with gains reduced when a short-sequence workload and large available cache make serving compute-bound.[^pagedattention-2023]

Its KV-cache breakdown reports 96.3% of vLLM cache capacity holding token states, versus 20.4%, 26.8%, and 38.2% for Orca Max, Pow2, and Oracle respectively in that experiment. These figures measure the paper's specific allocation designs and workload, rather than a universal utilization rate.[^pagedattention-2023]

Block sharing saved 6.1%–9.8% of cache blocks for parallel sampling and 37.6%–55.2% for beam search on the OPT-13B Alpaca trace; the corresponding ShareGPT ranges were 16.2%–30.5% and 44.3%–66.3%. For its shared-prefix translation experiment, vLLM reported $1.67\times$ throughput over Orca Oracle for an 80-token one-shot prefix and $3.58\times$ for a 341-token five-shot prefix.[^pagedattention-2023]

## Experimental scope

The evaluation used OPT 13B, 66B, and 175B plus LLaMA 13B on Google Cloud A2 instances with NVIDIA A100 GPUs. Workloads synthesized request lengths from ShareGPT and Alpaca and generated arrivals from Poisson distributions; its primary metric was mean end-to-end latency divided by output length. FasterTransformer used a custom dynamic-batching scheduler, and the unavailable Orca system was reimplemented with oracle, power-of-two reservation, and maximum-length reservation variants.[^pagedattention-2023]

Those choices make comparisons informative but bounded: Orca results depend on the authors' implementation and reservation assumptions, traces model lengths rather than original traffic timing, and normalized latency is not a complete user-facing latency or cost measure. The paper also measures a 15-minute trace rather than an hour for OPT-175B due to cost.[^pagedattention-2023]

## Costs and tuning

Paged block access imposed 20%–26% higher attention-kernel latency than the paper's highly optimized FasterTransformer kernel. Smaller blocks reduce final-block waste and improve sharing but can underuse GPU parallelism; larger blocks improve block processing but increase fragmentation and reduce sharing. The authors found block size 16 a practical default for their traces, not a universal optimum.[^pagedattention-2023]

The paper reports recomputation as more efficient than swapping for small blocks, where many small CPU–GPU transfers limit effective PCIe bandwidth; for block sizes 16–64, the two had comparable end-to-end performance. These recovery findings are hardware- and implementation-dependent.[^pagedattention-2023]

## Relationships

- **Evaluates:** [PagedAttention KV-cache serving](pagedattention-kv-cache-serving.md), including its demand allocation, block sharing, preemption, and kernel trade-offs.[^pagedattention-2023]
- **Contextualizes:** [KV caching](kv-caching.md): cache capacity and allocation efficiency constrain concurrent decoding even when per-token K/V computation is avoided.[^pagedattention-2023]

[^pagedattention-2023]: Kwon et al., “Efficient Memory Management for Large Language Model Serving with PagedAttention,” SOSP 2023, [source](../raw/arXiv-2309.06180v1/main.tex), Sections 6–7, Figures 1, 8–14, and Table 1.
