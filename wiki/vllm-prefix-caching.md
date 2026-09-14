---
type: Concept
title: vLLM Prefix Caching
description: Enabling, workloads, limits, and hash-based full-block reuse in vLLM v1 with LRU eviction, touch-on-hit allocation, cache-salt isolation, and Mamba fine-grained option.
tags: [vllm, kv-cache, prefix-caching, inference-optimization]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:01:59Z }
sources:
  - id: prefix-cache
    resource: ../raw/vllm/design/prefix_caching.md
    title: Automatic Prefix Caching
  - id: apc-feature
    resource: ../raw/vllm/features/automatic_prefix_caching.md
    title: Automatic Prefix Caching
---

vLLM reuses KV cache for shared prompt prefixes by hashing each full KV block on its tokens plus prefix history, looking hits up in the v1 KV cache manager, and evicting through an LRU free queue[^prefix-cache]. Automatic Prefix Caching (APC) lets a new query reuse that cached KV and skip computation of the shared part when it shares a prefix with an existing query[^apc-feature].

## Enabling

Set `enable_prefix_caching=True` in the vLLM engine to enable APC[^apc-feature].

## Hash key

Only full blocks are cached. Block `n` is identified by `hash(parent_hash, block_tokens, extra_hashes)`[^prefix-cache]:

- **Parent hash:** hash of the preceding block, chaining prefix history.
- **Block tokens:** exact token tuple in the block, reducing collision risk.
- **Extra hashes:** values needed for uniqueness such as LoRA IDs, multimodal input hashes, and multi-tenant `cache_salt`.

### Hash algorithms

As of v0.11 the default is `sha256`, addressing earlier collision risk. For `vllm serve`, `--prefix-caching-hash-algo` selects[^prefix-cache]:

- `sha256` (default): Python `pickle` serialization; may not reproduce across Python or vLLM versions.
- `sha256_cbor`: `cbor2` serialization; reproducible and cross-language compatible, recommended for deterministic caching.
- `xxhash`: pickle plus 128-bit xxHash; faster but non-cryptographic. The source warns collisions, however unlikely, can cause undefined behavior or leak private data in multi-tenant settings — weigh speed against risk. Requires optional `xxhash` package.
- `xxhash_cbor`: canonical CBOR plus xxHash for reproducible hashing. Requires optional `xxhash` package.

### Multimodal example

Image placeholders expand to many `<P>` tokens replaced by image embeddings at prefill. Placeholders alone cannot distinguish images, so the frontend image-processor hash is added as `extra hash` on every block covering placeholders[^prefix-cache].

## Cache isolation

A per-request `cache_salt` is injected into the first block hash, so only requests sharing the salt reuse blocks. This limits timing-based cache-probing attacks while preserving reuse inside a trust group[^prefix-cache].

## Data structures

Prefix caching lives in the KV cache manager around `KVCacheBlock`[^prefix-cache]:

- `block_id`: immutable identifier.
- `block_hash`: assigned when full, cleared on eviction.
- `ref_cnt`: number of requests currently using the block.
- `prev_free_block` / `next_free_block`: doubly linked free-queue pointers.

Design points[^prefix-cache]:

- All blocks are preallocated as a pool at manager init, avoiding runtime object creation and simplifying tracking.
- Intrusive linked-list pointers give O(1) move-from-middle-to-tail without a separate `deque` wrapper.

Manager components[^prefix-cache]:

- **Block pool:** list of all `KVCacheBlock`.
- **Free block queue:** head/tail pointers only.
- **Cached blocks:** hash key to block IDs.
- **Request blocks:** request ID to allocated block IDs.

## Operations

### New-request allocation

1. `get_computed_blocks()` hashes prompt tokens and looks up cached blocks[^prefix-cache].
2. `allocate_slots()`:
   1. Computes newly required blocks; aborts if insufficient free blocks.
   2. Touches computed blocks: increments `ref_cnt`, removes unused-but-cached blocks from the free queue so they cannot be evicted mid-allocation.
   3. Pops free-queue heads for new blocks; popping a cached head evicts it from future reuse.
   4. Immediately caches any allocated block already full, making it reusable within the same batch.

### Running-request allocation

Calls `allocate_slots()` only: check capacity, pop free heads with the same evict-on-pop rule, append token IDs, and cache newly completed blocks[^prefix-cache].

### Duplicated blocks

With block size 4, prompt `ABCDEF`, and greedy decode `GHI`, request 1 caches `ABCD` and `EFGH`. A repeat request reuses block 0 but allocates a new block 3 for `EFG[H]`, duplicating block 1's hash. vLLM v0 freed block 3 and rewrote the table to `[0, 1]`; vLLM v1 block tables are append-only, so the duplicate persists until request free[^prefix-cache].

### Free

On request completion, blocks with `ref_cnt == 0` return to the free-queue tail in reverse order: later blocks hash more tokens, are less reusable, and should therefore be evicted first[^prefix-cache].

### Eviction (LRU)

When the free-queue head is cached, reuse requires eviction[^prefix-cache]:

1. Pop head (least recently used).
2. Remove its ID from the cached-blocks map.
3. Clear its block hash.

## End-to-end example

With block size 4 and 10 blocks, the source traces[^prefix-cache]:

- **Time 1:** empty cache, request 0 allocates 4 blocks; 3 full blocks cached, 4th partial.
- **Time 2:** request 0 fills block 3, caches it, allocates block 4.
- **Time 3:** request 1 with 14 tokens and a 10-token shared prefix hits only the first 2 blocks, because the 3rd block matches 2 of 4 tokens.
- **Time 4:** request 0 freed; its blocks 2–4 return in reverse order, while blocks 0–1 stay out of the free queue because request 1 holds them.
- **Time 5:** request 1 freed.
- **Time 6:** request 2 with 29 tokens and a 12-token shared prefix touches hits 0–2 out of the free queue before allocating, so allocation reuses 0–2 and evicts 8 of the remaining free heads.

## Example workloads

- **Long document query:** repeated queries against the same long document such as a software manual or annual report. APC processes the document only once; later requests reuse its KV cache instead of recomputing it, with much higher throughput and lower latency[^apc-feature].
- **Multi-round conversation:** repeated turns in the same chat session. APC reuses processing results for chat history across future rounds, with much higher throughput and lower latency[^apc-feature].

## Limits

APC generally does not reduce vLLM performance. It shortens query processing (the prefilling phase) but not new-token generation (the decoding phase)[^apc-feature]. Expect little gain when:

- vLLM spends most time generating answers, for example when answers are long.
- New queries share no prefix with existing queries, so no computation can be reused[^apc-feature].

## Hybrid Mamba fine-grained prefix cache

Under `--mamba-cache-mode align`, Mamba state is stored only on the Mamba block grid, so a prefix-cache hit can resume only at a block boundary[^apc-feature]. `--enable-mamba-fine-grained-prefix-cache` additionally stores a checkpoint at the shared-prefix junction — the point where an earlier request with the same prefix stopped — so requests whose shared prefix ends inside a block can still reuse it[^apc-feature].

This helps when many requests share a long system prompt and then diverge. It is off by default and takes effect only when all of the following hold[^apc-feature]:

- `--mamba-cache-mode align`
- EAGLE/MTP speculative decoding on the Mamba group
- `--prefix-match-unit` smaller than the Mamba block size
- the model does not use multi-module MTP

```bash
vllm serve <hybrid-model> \
    --mamba-cache-mode align \
    --prefix-match-unit 64 \
    --enable-mamba-fine-grained-prefix-cache
```

`--prefix-match-unit` sets the granularity at which prefix-cache keys are computed and is required for the fine-grained behavior. When unset it defaults to the greatest common divisor of the prefix-cacheable KV cache group block sizes; under `align` that is the block size itself, so no sub-block boundary exists and the flag has no effect[^apc-feature].

Choose a value that divides the block size of every prefix-cacheable KV cache group and is a multiple of the per-state compression ratio for models that use one, such as sparse MLA. vLLM validates both at startup and names the offending sizes in the error. Read the served block size from the startup log; 64 is a reasonable starting point[^apc-feature].

## Relationships

- Uses [vLLM Hybrid KV Cache Manager](vllm-hybrid-kv-cache-manager.md) intersection logic for models with multiple attention types; this concept covers the base full-attention hash, allocation, free, and eviction mechanism that hybrid coordinators extend. The Mamba fine-grained checkpoint extends that hybrid coverage to shared prefixes ending inside a Mamba block[^apc-feature].

## Coverage limits

- Referenced diagrams for component overview, free queue, and example steps were absent from `raw/` and were not inspected[^prefix-cache].
- The referenced offline example `examples/features/automatic_prefix_caching/automatic_prefix_caching_offline.py` was not present under `raw/` and was not inspected[^apc-feature].

[^prefix-cache]: Automatic Prefix Caching — `../raw/vllm/design/prefix_caching.md`, hash construction and algorithms, multimodal example, cache isolation, data structures, allocation, duplicated blocks, free, eviction, and end-to-end example sections.

[^apc-feature]: Automatic Prefix Caching — `../raw/vllm/features/automatic_prefix_caching.md`, APC definition, `enable_prefix_caching` enablement, hybrid Mamba fine-grained prerequisites and `--prefix-match-unit` guidance, example workloads, and prefill-only limits.
