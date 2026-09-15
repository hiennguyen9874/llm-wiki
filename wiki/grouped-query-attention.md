---
type: Concept
title: Grouped-Query Attention
description: Intermediate attention between MHA and MQA that shares KV heads across query groups to cut KV-cache and decode bandwidth with near-MHA quality.
tags: [attention, gqa, mqa, kv-cache, inference, long-context]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T23:30:00Z }
sources:
  - id: gqa-syn
    resource: ../raw/GQA.md
    title: GQA synthesis (Vietnamese summary of Ainslie et al. 2023)
---

Grouped-Query Attention (GQA) splits query heads into groups sharing one key/value head per group, giving a tunable point between Multi-Head Attention (MHA) quality and Multi-Query Attention (MQA) decode efficiency, plus a cheap MHA-checkpoint conversion via mean-pooled uptraining[^gqa-syn].

## Definitions: MHA, MQA, GQA

For hidden size `d_model`, `H` query heads, head dim `d_h = d_model / H`, head `i` computes `O_i = softmax(Q_i K^T / sqrt(d_h) + M) V` then concatenates and projects with `W^O`[^gqa-syn].

- **MHA:** `H_Q = H_K = H_V = H`. Every query head has its own K/V projection[^gqa-syn].
- **MQA:** `H_Q = H`, `H_K = H_V = 1`. All query heads share one K/V pair, cutting KV cache roughly `H`-fold but forcing all queries through one K/V subspace[^gqa-syn].
- **GQA:** `H_Q = H`, `H_K = H_V = G`, with group ratio `R = H / G`. Query head `i` uses KV head `g(i) = floor(i / R)`: `O_i = softmax(Q_i K_g(i)^T / sqrt(d_h)) V_g(i)`[^gqa-syn].

Boundary cases: `G = H` recovers MHA; `G = 1` recovers MQA, so GQA is the spectrum `MHA <-> GQA <-> MQA`[^gqa-syn].

Example from the source: `H = 32, G = 8` gives `R = 4` — 32 query heads, 8 K heads, 8 V heads, 4 queries per KV head[^gqa-syn].

```text
MHA: Q0->K0,V0; Q1->K1,V1; ... (8 query heads, 8 KV heads)
GQA-4: Q0,Q1->K0,V0; Q2,Q3->K1,V1; Q4,Q5->K2,V2; Q6,Q7->K3,V3
MQA: Q0..Q7->K0,V0
```

Sharing is K/V-only: queries in one group keep separate `W_i^Q`, scores, distributions, and outputs, so they can attend to different positions through the same K/V space[^gqa-syn].

## Why it matters for decode

Autoregressive decode reads the full K/V history per new token, so long context or large batch is often memory-bandwidth-bound (HBM/VRAM to compute), not FLOP-bound[^gqa-syn].

GQA reduces KV heads, which reduces KV-cache size, per-token KV bytes read, and memory needed for long context or large batches[^gqa-syn].

## KV-cache saving

Decoder-only estimate (ignoring implementation detail), with layers `L`, batch `B`, length `S`, KV heads `H_KV`, head dim `d_h`, bytes/element `b`[^gqa-syn]:

```text
M_KV ~= 2 * L * B * S * H_KV * d_h * b   (factor 2 for K and V)
M_MHA = 2 * L * B * S * d_model * b
M_GQA / M_MHA = H_KV / H_Q = 1 / R
```

For `32` query heads and `8` KV heads the cache is ~25% of MHA, about a 4x reduction[^gqa-syn].

Worked example in the source (`L=32, S=4096, B=1, H_Q=32, d_h=128, FP16/BF16`): MHA ~2 GiB, GQA-8 ~512 MiB, MQA ~64 MiB for KV cache alone, excluding weights, transient activations, and framework overhead[^gqa-syn].

## FLOPs versus bandwidth

K/V projections shrink from `R^(d_model x d_model)` toward `R^(d_model x (H_KV * d_h))`, so their parameters and FLOPs fall by `H_KV / H_Q`[^gqa-syn].

But all `H_Q` query heads still compute separate scores and distributions, so attention-score work does not fall `R`-fold; the dominant decode win is fewer KV bytes read, not a proportional FLOP cut[^gqa-syn].

## MHA-to-GQA conversion and uptraining

The paper's second contribution is converting a trained MHA checkpoint without full retraining: for GQA group `G_j`, initialize the new K/V projections by mean-pooling the member MHA projections, keep Q and output projections, then continue pretraining briefly[^gqa-syn]:

```text
W_j^{K,GQA} = mean_{i in G_j} W_i^{K,MHA}
W_j^{V,GQA} = mean_{i in G_j} W_i^{V,MHA}
```

Mean pooling beat single-head selection, which beat random init; the authors' interpretation is that averaging preserves more of the original checkpoint[^gqa-syn].

After conversion the model is "uptrained" on the same pretraining recipe/data with fraction `alpha` (e.g. `alpha = 0.05` means ~5% of original steps/compute). In the main T5-XXL run this was ~600 TPUv3 chip-days; 5% gave a large gain with diminishing returns to 10%[^gqa-syn].

Practical note: mean-pool alone without continued pretraining is not expected to reach full quality[^gqa-syn].

## Experimental setup and headline result

Setup was T5.1.1, mainly MHA-Large, MHA-XXL, uptrained MQA-XXL, and uptrained GQA-8-XXL, applied to decoder self- and cross-attention but not encoder self-attention (encoder runs in parallel, so decode bandwidth is not the same bottleneck). Tasks included CNN/DailyMail, arXiv, PubMed, MediaSum, Multi-News summarization, WMT14 En-De, and TriviaQA; timing was on TPUv4 with per-model parallelization tuning[^gqa-syn].

| Model | Inference time | Mean score |
|---|---|---:|
| MHA-Large | 0.37 s | 46.0 |
| MHA-XXL | 1.51 s | 47.2 |
| MQA-XXL | 0.24 s | 46.6 |
| GQA-8-XXL | 0.28 s | 47.1 |

In this setup GQA-8 was near MQA speed (0.28 vs 0.24 s), ~5.4x faster than MHA-XXL (1.51/0.28), and near MHA-XXL quality (47.1 vs 47.2), above MQA-XXL (46.6)[^gqa-syn].

This speedup is benchmark-specific; it depends on hardware, batch, length, kernels, sharding, and serving stack and must not be reused as a universal factor[^gqa-syn].

## Why G = 8 and tensor-parallel fit

The authors swept `G in {1,4,8,16,32,64}` (1 = MQA, 64 = MHA in that config): moving 1 -> 4 or 8 added relatively little overhead, while approaching MHA raised decode time steeply, so 8 was chosen as the operating point[^gqa-syn].

`8` is not a universal optimum; what matters is the ratio `R = H_Q / H_KV` conditioned on `H_Q`, `d_h`, model size, context, and tensor parallelism[^gqa-syn].

MQA's single KV head may need replication across shards, wasting resources; GQA's multiple KV heads distribute more naturally (e.g. 8 KV heads over 8 TP ranks, implementation-dependent). Practical sizing seeks `H_Q % H_KV == 0` and ideally `H_KV % TP == 0` or an explicit replicate/shard plan[^gqa-syn].

## Quality view

Think of `G` as a capacity knob: MHA gives each query its own `(Q_i,K_i,V_i)` at high memory cost; MQA forces `(Q_i,K,V)` through one shared pair; GQA gives several `(Q_i,K_g,V_g)` subspaces without one pair per query[^gqa-syn].

GQA can still lose quality versus MHA because K/V capacity falls; the paper's claim is only that GQA-8 with proper uptraining lost very little on its benchmarks, not that every model, head count, dataset, or length preserves quality[^gqa-syn].

## Prefill versus decode

Prefill processes the whole prompt in parallel and can be compute-heavy; GQA still saves K/V projection cost and KV bytes written, but the speedup is usually smaller than in decode[^gqa-syn].

Decode handles one new query token against the full history, where KV bandwidth dominates, so GQA helps most for long context, large-batch decode, continuous batching, multi-request serving, and VRAM/bandwidth-limited systems[^gqa-syn].

## Implementation pitfall

Logical repeat is `q: [B,H_Q,Tq,D]`, `k,v: [B,H_KV,Tk,D]`, `repeats = H_Q // H_KV`; a naive implementation physically materializes `[B,H_Q,Tk,D]` K/V copies, which is mathematically correct but regrows temporary memory and bandwidth and erases much of the GQA win[^gqa-syn].

```python
assert num_query_heads % num_kv_heads == 0
repeats = num_query_heads // num_kv_heads
k_for_queries = repeat_kv_heads(k, repeats)  # prefer broadcast/view, not a copy
v_for_queries = repeat_kv_heads(v, repeats)
scores = q @ k_for_queries.transpose(-1, -2) / sqrt(q.shape[-1])
return softmax(scores, dim=-1) @ v_for_queries
```

Efficient serving uses broadcast/views, grouped kernels, paged-attention kernels with `num_kv_heads` support, or FlashAttention kernels with GQA/MQA paths[^gqa-syn].

## When to use MHA, GQA, or MQA

| Architecture | Quality/capacity | KV cache | Decode |
|---|---|---|---|
| MHA | Highest structural | Largest | Usually slowest |
| GQA | Near MHA | Down by `H_Q / H_KV` | Fast, balanced |
| MQA | Strongest sharing | Smallest | Usually cheapest |

MHA fits when maximum quality outweighs serving cost or context is short; GQA is the common production balance for long context and high throughput without MQA's extreme sharing; MQA fits when memory/latency dominates and its quality cost is acceptable or handled in pretraining[^gqa-syn].

## Limitations stated in the paper

Experiments were mainly encoder-decoder T5, not decoder-only LLMs; there was no full from-scratch GQA comparison at equal compute; summarization relied heavily on ROUGE; long-generation quality is intrinsically hard to evaluate; and timing is TPU/parallelization-specific. The claim that decoder-only models may benefit more is the authors' expectation in limitations, not a result proven by the paper's own runs[^gqa-syn].

## Relationships

- Related to [Multi-Query Attention](multi-query-attention.md) — synthesis: single-KV-head endpoint (`H_KV = 1`) of the MHA-GQA-MQA spectrum defined above; that page carries the Shazeer 2019 definition, KV-saving derivation, decode-bandwidth analysis, and quality limits.
- Contrasts with [FlashAttention Exact IO-Aware Attention](flashattention.md) — synthesis: GQA shrinks KV-head count and cache/bandwidth; FlashAttention reorders exact attention IO without changing head count, so `GQA + FlashAttention` is complementary.
- Uses [vLLM Paged Attention Kernel](vllm-paged-attention-kernel.md) — synthesis: paged serving kernels consume the shrunken GQA KV layout during decode.
- Uses [vLLM Decode Context Parallelism](vllm-decode-context-parallelism.md) — synthesis: that page's GQA TP-duplication rule (`tp // num_key_value_heads`) is the distributed consequence of the head counts defined here.
- Uses [vLLM Attention Backends](vllm-attention-backends.md) — synthesis: backend support for MHA/MQA/GQA layouts determines whether the theoretical cache saving is realized in serving.
- Uses [SGLang Attention Backends](sglang-attention-backends.md) — synthesis: same backend-selection point on the SGLang serving path.

## Coverage limits

- Single Vietnamese synthesis file read in full; no local attachments were referenced.
- External arXiv links for the GQA, Transformer, and MQA papers were not independently inspected; paper attributions, T5/TPU figures, timing, and score tables above follow the raw synthesis, not direct paper measurement.
- Worked GiB/MiB cache figures are the source's estimates for KV cache only.
- No secrets, credentials, or PII were found in the source.

[^gqa-syn]: GQA synthesis — `../raw/GQA.md`.
