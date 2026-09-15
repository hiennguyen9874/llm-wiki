---
type: Concept
title: KV Cache Compression and Optimization
description: Taxonomy, methods, selection guidance, and evaluation metrics for compressing and managing LLM KV cache.
tags: [kv-cache, inference, quantization, attention, serving]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T00:00:00Z }
sources:
  - id: kv-compression
    resource: ../raw/KVCacheCompressionOptimization.md
    title: KV Cache Compression and Optimization synthesis
---

Durable synthesis of two KV-cache surveys (Liu et al. arXiv 2508.06297 review and arXiv 2412.19442 management survey): KV cache removes recompute in autoregressive decoding but becomes the memory and bandwidth bottleneck at long context or high concurrency, addressed by keeping fewer tokens, storing each token cheaper, generating less KV by design, and managing placement better, usually as a hybrid adaptive pipeline rather than one technique[^kv-compression].

## KV cache and sizing

In decoder inference, past keys and values do not change, so only the new token's K/V is computed and history is reused from cache[^kv-compression].

Standard MHA sizing is approximately:

```text
2 × L × B × S × H_kv × d_h × bytes
```

where the factor 2 covers K and V, L layers, B batch, S context tokens, H_kv KV heads, d_h head dim[^kv-compression].

Source worked example: 32 layers, hidden 4096, FP16, batch 1, 32k context in MHA gives about 16 GiB for one request, before weights, activations, workspace, fragmentation, and concurrency[^kv-compression].

Scaling correction: cache grows linearly with context length and batch size, not exponentially; dense prefill attention compute is the quadratic term[^kv-compression].

## Optimization objective

Methods trade off memory, accuracy, latency, and throughput[^kv-compression].

A good method must avoid degrading generation quality, losing early-context or needle-in-a-haystack retrieval, adding selection or decompression overhead that erases savings, breaking kernel efficiency, or breaking batching and PagedAttention compatibility[^kv-compression].

No single method fits all workloads; choice depends on context length, hardware, attention architecture, and accuracy needs[^kv-compression].

## Keep fewer tokens: selection and eviction

Keep subset `I` with `|I| << S` of `{(K_i,V_i)}` judged likely to be attended again[^kv-compression].

- **Sliding window:** keep only the newest W tokens; fixed memory and simple, but loses distant information for retrieval, code, and long documents[^kv-compression].
- **Sink tokens:** keep a few initial tokens plus a recent window, stabilizing heads that attend strongly to early positions[^kv-compression].
- **Heavy-hitter eviction:** for example H2O keeps recent tokens plus tokens with large cumulative attention `score(i) = sum_{t>i} A_{t,i}`; exploits attention sparsity but past attention may not predict future importance and score maintenance adds overhead[^kv-compression].
- **Observation-window selection:** for example SnapKV runs full prefill, scores prompt tokens by attention from the final prompt window, keeps top-k, and discards the rest once before decoding; one-time selection cost but permanently evicted tokens cannot be recovered later[^kv-compression].
- **Head-aware selection:** for example RazorAttention gives retrieval heads full or larger cache and compresses local heads harder, often with compensation tokens; a nonuniform per-head budget usually beats a uniform one[^kv-compression].

The broader survey distinguishes static selection, dynamic selection with permanent eviction, and dynamic retrieval without permanent deletion[^kv-compression].

## Allocate budget across layers and heads

Selection answers which tokens to keep; allocation answers how many tokens each layer or head may keep under `sum C_{l,h} <= C_total`[^kv-compression].

Layers and heads differ: diffuse-attention layers and retrieval heads need more budget than focused or local heads[^kv-compression].

Examples are ZigZagKV with uncertainty-based dynamic allocation, plus SqueezeAttention and PyramidInfer exploiting cross-layer heterogeneity[^kv-compression].

A pyramid-shaped `C_1 > C_2 > ... > C_L` schedule is one option, but the best shape depends on model and task[^kv-compression].

## Store each token cheaper: quantization

Keep all tokens but use fewer bits per element, with dequantization `x_hat = s q + z`[^kv-compression].

Ideal savings versus FP16 are about 2x for INT8, 4x for INT4, and 8x for INT2, reduced in practice by scales, zero points, metadata, alignment, and residuals or outliers[^kv-compression].

- **K versus V asymmetry:** key error perturbs logits before softmax and can be amplified, while value error enters only linearly through the attention-weighted sum, so many methods give K higher precision or different grouping than V; examples include KIVI, KVQuant, QAQ, AlignedKV, and AsymKV[^kv-compression].
- **Per-token versus per-channel:** per-token scales suit large magnitude shifts across tokens; per-channel scales suit persistent outlier channels; KIVI is noted for 2-bit asymmetric treatment exploiting different K/V outlier distributions[^kv-compression].
- **Residual cache:** keep R recent tokens in FP16 and quantize older blocks, converting a full block only when the buffer fills, reducing per-token update overhead and protecting recent context[^kv-compression].

Production caveat: quantization only speeds up serving when saved memory bandwidth exceeds dequantization, bit-unpacking, layout, and kernel-launch costs; a high paper compression ratio without fused kernels can use less VRAM yet run slower[^kv-compression].

## Merge similar tokens

Replace a similar-token group G with a weighted representative K/V instead of deleting it outright[^kv-compression].

This preserves more information than hard eviction and exploits redundancy, but changes attention distribution, adds clustering or similarity-search cost, and interacts poorly with positional encodings such as RoPE[^kv-compression].

EMS is cited as an evict-then-merge adaptive per-head strategy combining global-local importance[^kv-compression].

## Low-rank and sparse coding

Approximate `K ~= U_K R_K` with rank `r << d_h`, storing `Sr + r d_h` instead of `S d_h`, or use sparse coding `K ~= D A` with shared dictionary D and sparse coefficients A[^kv-compression].

This can reach high ratios more softly than eviction, but projection and reconstruction cost compute, online per-token updates are hard, specialized kernels are needed, and suitable rank varies by layer, head, and request[^kv-compression].

## Generate less KV by design

- **Multi-Query Attention:** `H_kv = 1` shared across query heads, cutting cache by about `H_q` versus MHA at some representation cost[^kv-compression].
- **Grouped-Query Attention:** `1 < H_kv < H_q`, cutting cache by about `H_q / H_kv`; for example 32 query heads with 8 KV heads gives about 4x; usually the cheapest stable saving when architecture can be chosen up front[^kv-compression].
- **Cross-layer sharing:** reuse KV across nearby layers with similar representations, for example KVSharer; saves memory and speeds inference and composes with other methods, but over-sharing loses depth-specific representations[^kv-compression].

## Manage placement better

- **Paged cache:** split cache into blocks or pages instead of contiguous per-sequence reservation, reducing fragmentation, enabling dynamic allocation, mixed-length batching, and prefix sharing; PagedAttention in vLLM is the canonical example[^kv-compression].
- **Prefix caching:** compute shared prefix KV once and reuse it across requests; does not shrink one request's cache but cuts prefill compute, time-to-first-token, and aggregate memory when pages are shared[^kv-compression].
- **Offloading and hierarchy:** keep hot KV on GPU HBM and colder KV on CPU, NVMe, or remote memory with prefetch; the bottleneck shifts to `transfer_time ~= KV_bytes / interconnect_bandwidth`, so slow retrieval can outweigh attention savings[^kv-compression].

Memory management and scheduling are the two system-level pillars in the broader survey[^kv-compression].

## Review taxonomies compared

Liu et al. 2025 organizes work into selective compression, quantization compression, attention compression, and hybrid methods, with future work on hybrid optimization, request-adaptive dynamic policy, and software-hardware co-design[^kv-compression].

The broader survey uses token-level, model-level, and system-level tiers[^kv-compression].

Source assessment: the Liu taxonomy is accessible but selective and attention compression overlap since methods such as H2O, RazorAttention, and PyramidInfer span both; cross-paper throughput and quality tables are not apples-to-apples because models, context lengths, GPUs, benchmarks, and budgets differ; and kernel-level costs such as noncontiguous gather, top-k, dequantization, irregular sparsity, CPU-GPU transfer, and missing fused kernels are under-analyzed[^kv-compression].

## Practical selection and pipeline

| Case | Suitable direction |
|---|---|
| Model already uses GQA or MQA | Start with paged cache and prefix caching |
| Must stay near full-cache quality | INT8/INT4 quantization or light hybrid |
| Very long context with retrieval | Head-aware selection or dynamic retrieval |
| Ordinary chat | Recent window plus sink or heavy-hitter tokens |
| Small VRAM | Quantization plus offload |
| Large batch serving | PagedAttention plus continuous batching plus prefix sharing |
| Reusable RAG prefix or blocks | Prefix or block cache such as CacheBlend |
| Edge device | GQA/MQA plus low-bit KV quantization |
| Accuracy-critical reasoning | Conservative compression preserving retrieval heads and recent tokens |
| Maximum ratio at any cost | Hybrid pruning plus quantization with careful benchmarking |

Recommended order is `GQA -> paged KV -> prefix cache -> INT4/INT8 -> head-aware eviction`, because architecture and layout changes lose the least quality, quantization preserves all tokens, and eviction is riskiest since deleted information is hard to recover[^kv-compression].

## Evaluation metrics

Report memory, quality, latency, throughput, and overhead together, not gigabytes saved alone[^kv-compression].

- **Memory:** compression ratio `M_full / M_compressed`.
- **Quality:** perplexity, exact match or F1, LongBench, RULER, needle-in-a-haystack, code completion, summarization quality.
- **Latency:** time-to-first-token, time-per-output-token, inter-token latency, prefill latency, decode latency.
- **System:** tokens per second, requests per second, maximum concurrency, goodput under latency SLO.
- **Overhead:** selection time, quantize or dequantize cost, migration, metadata memory, kernel efficiency.

## Relationships

- Related to [AI Inference, KV Cache, and Serving Optimizations](ai-inference-kv-cache-fundamentals.md) — synthesis: per-token sizing, paged allocation, prefix reuse, and weight-quantization baseline extended here into KV-specific compression taxonomy.
- Related to [PagedAttention for LLM Serving](paged-attention.md) — synthesis: block tables, on-demand growth, copy-on-write sharing, batching, preemption, and serving evaluation behind the paged-cache summary above.
- Uses [Grouped-Query Attention](grouped-query-attention.md) — synthesis: MQA/GQA head-sharing mechanism behind the generate-less-KV savings above.
- Uses [vLLM Paged Attention Kernel](vllm-paged-attention-kernel.md) — synthesis: paged block layout behind the system-level paging claim above.
- Uses [vLLM Prefix Caching](vllm-prefix-caching.md) — synthesis: hash, allocation, eviction, and workload mechanics behind the shared-prefix reuse claim above.
- Uses [vLLM Quantized KV Cache](vllm-quantized-kv-cache.md) — synthesis: FP8 formats, calibration, layer skips, and backend constraints behind production KV-quantization limits above.
- Related to [SGLang Quantized KV Cache](sglang-quantized-kv-cache.md) — synthesis: FP8/FP4 formats and backend constraints relevant to the store-each-token-cheaper section above.
- Related to [vLLM TurboQuant KV-Cache Quantization](vllm-turboquant-kv-cache.md) — synthesis: storage-only low-bit KV evidence relevant to ratio-versus-throughput caveats above.
- Related to [Distributed Inference Optimization Levers](distributed-inference-optimization-levers.md) — synthesis: disaggregation and tiered/shared KV-cache decisions extending the offload and hierarchy section above.
- Uses [vLLM KV Offloading Connector](vllm-kv-offloading.md) — synthesis: CPU and tiered offload mechanics behind the hierarchical-cache transfer trade-off above.

## Coverage limits

- Source file was read in full; the two cited arXiv surveys were used only through that synthesis and were not independently re-read, so method details and benchmark numbers are source-reported[^kv-compression].
- No local attachments were referenced by the raw file.
- All formulas, 16 GiB example, method-to-paper mappings such as H2O, SnapKV, RazorAttention, ZigZagKV, KIVI, EMS, and KVSharer, taxonomy comparisons, selection table, pipeline order, and metric lists are synthesis claims and were not independently verified.
- No secrets, credentials, tokens, private keys, or PII were found in the source.

[^kv-compression]: KV Cache Compression and Optimization synthesis — `../raw/KVCacheCompressionOptimization.md`, covering KV-cache rationale, linear sizing formula and 16 GiB example, memory-accuracy-latency-throughput objective, token selection and eviction, budget allocation, asymmetric and grouped quantization with residual cache, merging, low-rank and sparse coding, MQA/GQA/cross-layer design, paged/prefix/offload management, Liu 2025 versus token/model/system taxonomies, practical selection table and GQA-to-eviction pipeline, and evaluation metrics.
