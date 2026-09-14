---
type: Concept
title: vLLM Hybrid KV Cache Manager
description: Unified page-size grouping, per-group allocation, and intersected prefix caching for hybrid-attention models.
tags: [vllm, kv-cache, hybrid-models, prefix-caching]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: hybrid-kv
    resource: ../raw/vllm/design/hybrid_kv_cache_manager.md
    title: Hybrid KV Cache Manager
---

vLLM serves hybrid-attention models from one same-page-size block pool by partitioning layers into KV cache groups, allocating different block counts per group, and intersecting per-group prefix-cache hits[^hybrid-kv].

> [!warning] Early-stage design
> The source is based on vLLM commit `458e74` and warns the feature is early-stage and may change[^hybrid-kv].

## Hybrid models and requirements

Hybrid models combine multiple attention types in one model[^hybrid-kv]:

- Sliding-window + full attention: GPT-OSS, Gemma 2/3, Ministral, Cohere.
- Mamba + full attention: Bamba, Jamba, Minimax.
- Local chunked + full attention: Llama 4.

The manager must therefore allocate different slots per layer type — full layers reserve slots for all tokens, sliding-window layers only for the most recent `sliding_window_size` tokens — and apply layer-specific prefix-cache rules: full attention needs all prefix tokens resident, sliding-window only the last `sliding_window_size` tokens[^hybrid-kv].

## Definitions

- **KV hidden size:** bytes for one token's KV cache in one layer[^hybrid-kv].
- **Block:** unit of the memory pool; all blocks share one **page size**[^hybrid-kv].
- **Block size:** number of tokens per block[^hybrid-kv].
- **Page size:** `num_layers * block_size * kv_hidden_size`, where `num_layers` is context-dependent, not necessarily total model layers[^hybrid-kv].
- Do not confuse this with `KVCacheSpec.page_size_bytes`, defined as `block_size * kv_hidden_size`[^hybrid-kv].

## Allocation: one pool, unified page size

Full-attention-only page size is `block_size * num_hidden_layers * kv_hidden_size`. Hybrid models would naturally get mismatched page sizes because layer counts differ by attention type, so the design unifies them through KV cache groups[^hybrid-kv].

A KV cache group satisfies[^hybrid-kv]:

1. Identical attention type inside each group, so member layers need the same block count and can share block IDs without waste.
2. Identical page size across groups, since the pool has one page size.

### Regular and irregular layer ratios

- **Toy case:** 1 full + 3 sliding-window layers with equal hidden size use `page_size = kv_hidden_size * block_size`, allocating per layer[^hybrid-kv].
- **Regular pattern:** for example 20 sliding-window + 10 full layers, treat the model as a repeated 2:1 unit such as Gemma-2's 1:1 or Llama 4's 3 local : 1 full. Repeating one 2-sw + 1-full allocation 10 times gives `page_size = 10 * kv_hidden_size * block_size` and fewer allocator calls. With `block_size=16`, window 32, and length 112, the example needs 11 blocks: 0–6 for full, 7–8 and 9–10 for the two sliding-window groups[^hybrid-kv].
- **Irregular pattern:** Gemma-3-27B has 52 sliding-window + 10 full layers, which would otherwise yield many 2-layer groups. The heuristic uses group size `min(counts)`, here 10: one 10-layer full group, five 10-layer sliding-window groups, plus a final group of 2 sliding-window + 8 padding layers. The source notes this heuristic may change — for example 20 full + 30 sliding-window should use 10 rather than 20 — and the same padding path covers Case-2 models plus one Eagle speculative-decoding full layer[^hybrid-kv].

### Different hidden sizes and KV sharing

- **Hybrid Mamba:** Mamba state per token can greatly exceed attention `kv_hidden_size`. The current algorithm enlarges attention `block_size` until `block_size * kv_hidden_size_att >= state_size_mamba`, pads each Mamba state to that size, then applies the irregular-pattern grouping. This can exceed `block_size` 400; an alternative using `block_size * kv_hidden_size_att * num_attn_layers >= state_size_mamba` is work in progress[^hybrid-kv].
- **KV sharing:** for example Gemma-3n, layers reusing another layer's KV are ignored during allocation; the model runner patches the allocation onto sharing layers[^hybrid-kv].

## Prefix caching: per-group hits plus intersection

The block pool keys cached full blocks by `(block_hash, group_id)`, so identical tokens are cached and evicted independently per group. A request's cached prefix is the intersection of per-group hits[^hybrid-kv].

The prefix-caching section assumes `block_size=1`[^hybrid-kv].

- **Full attention only:** blocks cover all tokens; scan left-to-right and stop at the first miss[^hybrid-kv].
- **Sliding-window only:** vLLM allocates distinct blocks per token and frees blocks leaving the window instead of round-robin reuse, preserving prefix caching. Only the last `sliding_window_size - 1` tokens must be cached. With window 4 and a 15-token prompt, possible hit lengths include 5, 6, and 14, with 14 most efficient. Lookup scans right-to-left and exits on a match — the reverse of full attention — at the cost of scanning all tokens on the common no-match path[^hybrid-kv].
- **Full + sliding-window/efficient attention:** first take the longest full-attention hit left-to-right, then take the longest efficient-attention hit within that length right-to-left. The result is valid for both groups without enumerating all prefixes. This covers exactly two attention types as full + X, where X may be sliding-window, Llama-4 local attention, or Mamba; models without full attention or with more than two types are unsupported. Eviction uses one shared LRU queue; blocks enter it when freed by request completion or leaving the sliding window[^hybrid-kv].
- **Mamba:** prefix-caching support was work in progress; once done, Mamba + full models use the same full + X intersection[^hybrid-kv].

## Implementation layers and memory layout

Three layers[^hybrid-kv]:

- `KVCacheManager`: scheduler-facing interface.
- `KVCacheCoordinator`: combines per-group managers:
  - `KVCacheCoordinatorNoPrefixCache` when prefix caching is disabled.
  - `UnitaryKVCacheCoordinator` for one group, with no intersection.
  - `HybridKVCacheCoordinator` for exactly two groups containing one full-attention group plus one efficient-attention group; other multi-group shapes must disable prefix caching.
- `SingleTypeKVCacheManager`: per-group allocation and prefix logic, for example `FullAttentionManager` and `SlidingWindowManager`.

For `n` groups of `m` layers each, physical memory has `m` buffers (`KVCacheTensor`s), each shared by `n` layers — one from every group. In the 10-full + 20-sliding-window example, 10 buffers are each shared by 3 layers such as `full.0`, `sw.0`, and `sw.10`; pieces of size `block_size * kv_hidden_size` are selected by allocated `block_id`s, so one logical block maps to `m` physical pieces[^hybrid-kv].

## Coverage limits

- Referenced diagrams for grouping, full-attention and sliding-window prefix caching, overview, and memory layout were absent from `raw/` and were not inspected[^hybrid-kv].
- Referenced implementation classes and `prefix_caching.md` were not verified beyond this source[^hybrid-kv].

[^hybrid-kv]: Hybrid KV Cache Manager — `../raw/vllm/design/hybrid_kv_cache_manager.md`, What is a hybrid model, Definitions, Allocation, Prefix caching, and Implementation sections.
