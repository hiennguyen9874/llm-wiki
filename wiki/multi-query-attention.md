---
type: Concept
title: Multi-Query Attention
description: Shared single KV head across query heads that cuts KV-cache and decode bandwidth roughly H-fold at some representation cost.
tags: [attention, mqa, kv-cache, inference, decoding]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T23:30:00Z }
sources:
  - id: mqa-syn
    resource: ../raw/MQA.md
    title: MQA synthesis (Vietnamese summary of Shazeer 2019)
---

Multi-Query Attention (MQA) keeps many query heads but shares one key head and one value head across all of them (`H_Q = H`, `H_K = H_V = 1`), cutting KV-cache size and autoregressive decode bandwidth by roughly the query-head count at the cost of forcing all heads through one K/V subspace[^mqa-syn].

## Definitions: MHA versus MQA

For hidden size `d_model`, `H` query heads, and head dim `d_h = d_model / H`[^mqa-syn]:

- **MHA:** `Q_h = X W_h^Q`, `K_h = X W_h^K`, `V_h = X W_h^V` per head `h`; `O_h = softmax(Q_h K_h^T / sqrt(d_h)) V_h`; outputs concatenated and projected with `W^O`. Thus `H_Q = H_K = H_V = H`[^mqa-syn].
- **MQA:** `Q_h = X W_h^Q` stays per-head, but `K = X W^K` and `V = X W^V` are shared; `O_h = softmax(Q_h K^T / sqrt(d_h)) V`. Thus `H_Q = H`, `H_K = H_V = 1`[^mqa-syn].

The name means many query heads query the same K/V set, not one head containing many queries[^mqa-syn].

```text
MHA with 8 heads: Q1->K1,V1; Q2->K2,V2; ... Q8->K8,V8
MQA with 8 queries: Q1..Q8 -> shared K,V
```

MQA does not merge query heads; it removes the head dimension from K/V tensors only[^mqa-syn]. Query heads keep distinct distributions because `Q_1 != Q_2`, so `softmax(Q_1 K^T) != softmax(Q_2 K^T)`, but they aggregate the same value vectors[^mqa-syn].

## Why decode is memory-bandwidth-bound

Autoregressive decoding emits one token at a time and cannot precompute the next token[^mqa-syn]. Each layer caches prior K/V; each new token computes a new query, reads the full K/V history, scores, aggregates, then appends its K/V[^mqa-syn].

MHA cache shape is approximately `[B,L,S,H,d_h]` for batch `B`, layers `L`, context `S`, KV heads `H`, and head dim `d_h`[^mqa-syn]. Because this cache is re-read every decode step, data movement can dominate FLOPs, especially with long context, large batches, many layers, or limited HBM bandwidth[^mqa-syn].

## KV-cache saving

Approximate KV bytes with `H_KV` KV heads and `p` bytes per element[^mqa-syn]:

```text
KV bytes ~= 2 * B * L * S * H_KV * d_h * p   (factor 2 for K and V)
KV_MHA / KV_MQA = H_Q
```

Worked source example (`L=32`, `H_Q=32`, `d_h=128`, `S=4096`, FP16, `B=1`): MHA ~2 GiB versus MQA ~64 MiB, an ideal ~32x reduction for K/V tensors alone, excluding allocator, padding, metadata, and transient buffers[^mqa-syn].

## FLOPs versus bandwidth

MQA creates one K and one V vector per token instead of `H` each, reducing K/V projection cost, K/V parameters, cache size, and HBM/DRAM reads[^mqa-syn].

It does not remove query-side attention work: all `H` query heads still compute `Q_h K^T`, so the main decode win is fewer KV bytes read, not a proportional FLOP cut[^mqa-syn]. The source summarizes the original analysis as reducing the adverse memory-access component of incremental attention by roughly the head count `h`[^mqa-syn].

## Prefill versus decode

Prefill processes the whole prompt in parallel as large matrix multiplications and is often compute-heavy; MQA still saves K/V projection and bytes written, but less dramatically[^mqa-syn].

Decode uses one new query `[B,H,1,d_h]` against long K/V `[B,H,S,d_h]`, becoming many small matrix-vector operations with low arithmetic intensity; MQA shrinks the read side to `[B,1,S,d_h]`, which is why the paper targets incremental decoding[^mqa-syn].

A smaller cache also lets serving hold more concurrent sequences, improving system throughput beyond single-request latency[^mqa-syn].

## Original paper results

Source reports Shazeer 2019 experiments on a ~211M-parameter encoder-decoder Transformer (`d_model=1024`, 6 layers, 8 heads, head dim 128) on WMT14 English-German, with the MQA feed-forward network enlarged to match baseline parameter count[^mqa-syn].

| Model | Greedy BLEU | Beam-4 BLEU |
|---|---:|---:|
| MHA | 27.7 | 28.4 |
| MQA | 27.5 | 28.5 |

MQA was slightly lower with greedy decoding and about even with beam search in that setup; the source cautions one result does not mean MQA is generally better than MHA, only that quality loss was small there[^mqa-syn].

Decoder incremental cost on TPUv2 was reported as 46 us/token for MHA versus 3.8 us/token for MQA (~12.1x on that setup), and encoder plus 4-wide beam-search decoder as `(2.0 + 203)` versus `(1.6 + 32)` us/token[^mqa-syn]. These figures depend on hardware, batch, kernels, and implementation and must not be reused as a universal speedup[^mqa-syn].

On Billion Word language modeling, dev perplexity was 29.9 for MHA versus 30.2 for MQA; MQA beat naive alternatives such as directly reducing heads or shrinking K/V size in the paper's runs[^mqa-syn].

## Why sharing can cost quality

MHA lets heads specialize in syntax, coreference, position, entities, long-range versus local patterns through separate `(K_h,V_h)` spaces[^mqa-syn].

MQA imposes two limits[^mqa-syn]:

- **Key subspace:** all heads compare against the same K representation and cannot choose fully separate key spaces.
- **Value subspace:** even with different attention weights, heads aggregate the same V vectors.

Capacity loss matters most where tasks need many independent K/V representations[^mqa-syn].

## MQA in the MHA-GQA spectrum

With `H_Q` query heads and `H_KV` KV heads, `1 <= H_KV <= H_Q`: `H_KV = H_Q` is MHA, `1 < H_KV < H_Q` is GQA, and `H_KV = 1` is MQA[^mqa-syn].

The source notes the 2023 GQA paper positions GQA as near-MHA quality at near-MQA speed, including MHA-to-MQA/GQA conversion by uptraining on ~5% of original pretraining compute in its setup[^mqa-syn].

| Property | MHA | GQA | MQA |
|---|---|---|---|
| Query heads | `H` | `H` | `H` |
| KV heads | `H` | `G` | 1 |
| KV cache | Largest | Middle | Smallest |
| Representation capacity | High | Near MHA | Can be lower |
| Decode bandwidth | High | Lower | Lowest |
| Common operating point | Quality | Quality/speed balance | Speed/memory |

## Parameter impact

Ignoring bias, MHA attention is about `4 d_model^2` (`W^Q,W^K,W^V,W^O` each `d_model x d_model`), while MQA is about `2 d_model^2 + 2 d_model d_h` because `W^K,W^V` shrink to `d_model x d_h`[^mqa-syn].

Since `d_h = d_model / H`, this is `2 d_model^2 + 2 d_model^2 / H`; for `H=32` the attention-projection total falls from ~`4 d_model^2` to ~`2.0625 d_model^2`, but whole-LLM parameters fall much less because embeddings, feed-forward layers, and other blocks dominate[^mqa-syn]. The original paper enlarged MQA feed-forward layers to isolate architecture effects from parameter-count effects[^mqa-syn].

## Implementation sketch

```python
# x: [batch, seq, d_model]
q = q_proj(x).view(batch, seq, num_query_heads, head_dim)

# One KV head, logically broadcast to every query head
k = k_proj(x).view(batch, seq, 1, head_dim)
v = v_proj(x).view(batch, seq, 1, head_dim)

scores = einsum("bthd,bs1d->bhts", q, k)
weights = softmax(scores / sqrt(head_dim), dim=-1)
output = einsum("bhts,bs1d->bthd", weights, v)
```

Do not physically `repeat` K/V into `H` copies; use broadcast, grouped-query layout, or kernels with MQA/GQA paths, or the memory and bandwidth benefit is largely lost[^mqa-syn].

## When MQA helps most

Prefer MQA when token-generation speed, long context, large-batch serving, KV-cache capacity, concurrency, or memory-bandwidth-limited hardware dominates[^mqa-syn].

Expect less benefit when measuring prefill only, using very short sequences, staying compute-bound at small batch, running unoptimized MQA kernels, or when feed-forward layers or interconnect are the actual bottleneck[^mqa-syn].

## Limitations of the 2019 evidence

The source lists five scope limits: ~192-211M test models far below modern LLMs; mainly machine translation plus Billion Word runs; TPUv2/TPUv3 hardware; short 128-token timing context; and major later changes in kernels, quantization, paged KV cache, and serving systems[^mqa-syn].

The durable claim is architectural — KV-head count controls cache size and decode bandwidth — not a fixed speedup factor[^mqa-syn]. The paper's conclusion as reported is much lower incremental-inference memory-bandwidth demand with only a small quality drop on its tests[^mqa-syn].

## Relationships

- Related to [Grouped-Query Attention](grouped-query-attention.md) — synthesis: GQA generalizes this single-KV-head design to `1 < H_KV < H_Q` for a quality/efficiency balance; MQA is its `H_KV = 1` endpoint.
- Related to [AI Inference, KV Cache, and Serving Optimizations](ai-inference-kv-cache-fundamentals.md) — synthesis: fewer KV heads directly lowers the `num_kv_heads` term in that page's per-token cache formula and concurrency limits.
- Uses [KV Cache Compression and Optimization](kv-cache-compression-optimization.md) — synthesis: MQA is the generate-less-KV architectural option alongside quantization, eviction, merging, low-rank, cross-layer sharing, paging, prefix reuse, and offload.
- Uses [vLLM Paged Attention Kernel](vllm-paged-attention-kernel.md) — synthesis: paged serving kernels consume the shrunken MQA KV layout during decode.
- Uses [FlashAttention Exact IO-Aware Attention](flashattention.md) — synthesis: exact tiled IO-aware kernels are complementary because they reorder attention IO without changing the KV-head count reduced here.

## Coverage limits

- Single Vietnamese synthesis file read in full; no local attachments were referenced.
- External arXiv links for the MQA, Transformer, and GQA papers were not independently inspected; paper attributions, BLEU, perplexity, microsecond timings, model dimensions, and cache arithmetic above follow the raw synthesis, not direct paper measurement.
- Worked GiB/MiB cache figures are the source's estimates for K/V tensors only.
- No secrets, credentials, or PII were found in the source.

[^mqa-syn]: MQA synthesis — `../raw/MQA.md`.
