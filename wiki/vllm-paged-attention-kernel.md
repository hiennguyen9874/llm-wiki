---
type: Concept
title: vLLM Paged Attention Kernel
description: Historical vLLM multi-head query attention CUDA kernel over paged KV cache, covering query/key/value data paths, softmax reduction, and output writeback.
tags: [vllm, paged-attention, cuda, kv-cache]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T08:33:10Z }
sources:
  - id: paged-attn
    resource: ../raw/vllm/design/paged_attention.md
    title: Paged Attention
---

vLLM's historical paged-attention document explains the multi-head query attention CUDA kernel (`csrc/attention/attention_kernels.cu`) that operates directly on paged KV cache with separately blocked keys and values[^paged-attn].

> [!warning] Historical document
> The source warns it is based on the original vLLM paper and no longer describes current vLLM code[^paged-attn].

The document's stated purpose is a high-level implementation walkthrough — memory layout, fetch assignment, and reduction flow — while omitting details such as exact index arithmetic and dot-product internals[^paged-attn].

## Kernel signature

The kernel operates on four main global-memory arrays[^paged-attn]:

- `q` — `[num_seqs, num_heads, head_size]`
- `k_cache` — `[num_blocks, num_kv_heads, head_size/x, block_size, x]`
- `v_cache` — `[num_blocks, num_kv_heads, head_size, block_size]`
- `out` — `[num_seqs, num_heads, max_num_partitions, head_size]`

Compile-time parameters are `scalar_t` (e.g. FP16), `HEAD_SIZE`, `BLOCK_SIZE` (tokens per KV block), `NUM_THREADS` (threads per thread block), and `PARTITION_SIZE` (tensor-parallel GPU count; the document assumes 0/disabled)[^paged-attn].

Key and value caches use separate block layouts; the source stresses not to confuse vLLM paged-attention "block" with GPU "thread block"[^paged-attn].

## Execution and data vocabulary

- **Sequence:** one client request; because this is single-query attention, each sequence contributes one query token, so `num_seqs` equals tokens processed in the batch[^paged-attn].
- **Context:** previously generated tokens that the query attends over[^paged-attn].
- **Block:** KV-cache unit holding `BLOCK_SIZE` tokens for one head; a context may span several blocks (e.g. `BLOCK_SIZE=16`, `HEAD_SIZE=128` gives 2048 elements per block per head)[^paged-attn].
- **Vec:** elements fetched/computed together. Query/key `VEC_SIZE` is sized so each thread group fetches 16 bytes at once; value `V_VEC_SIZE` is sized so each thread fetches 16 bytes at once (e.g. FP16 + `THREAD_GROUP_SIZE=2` gives `VEC_SIZE=4`, `V_VEC_SIZE=8`)[^paged-attn].
- **Thread group:** `THREAD_GROUP_SIZE` threads jointly handling one query token against one key token; each thread handles a strided subset (e.g. group of 2 with head size 8: thread 0 takes indices 0,2,4,6 and thread 1 takes 1,3,5,7). Total elements per group is called `x`[^paged-attn].
- **Warp:** 32 threads executing together; each warp handles one query token against all key tokens of one block at a time, iterating over multiple blocks (e.g. 4 warps over 6 blocks: warp 0 takes blocks 0 and 4, warp 1 takes 1 and 5, warp 2 takes 2, warp 3 takes 3)[^paged-attn].
- **Thread block:** `NUM_THREADS` threads sharing shared memory and containing multiple warps; each handles one query token against a whole context[^paged-attn].
- **Grid:** `(num_heads, num_seqs, max_num_partitions)`; each thread block handles one head, one sequence, and one partition[^paged-attn].

## Query path

Each thread forms `q_ptr = q + seq_idx * q_stride + head_idx * HEAD_SIZE`, pointing at its assigned query token's `HEAD_SIZE` elements split into `HEAD_SIZE / VEC_SIZE` vecs[^paged-attn].

Query data is staged into shared memory as `Q_vec q_vecs[THREAD_GROUP_SIZE][NUM_VECS_PER_THREAD]`, with each vec on a different row owned by a different thread in the group so neighboring threads read neighboring memory (memory coalescing)[^paged-attn].

Within a warp, every thread group fetches the same query token but multiplies it against different key tokens[^paged-attn].

## Key path

Each thread forms `k_ptr` from `k_cache` plus physical block number, KV-head index, and in-block token offset (`physical_block_offset * x`), so `k_ptr` changes across iterations to visit different context tokens[^paged-attn].

Keys are staged into per-thread register memory as `K_vec k_vecs[NUM_VECS_PER_THREAD]` — registers rather than shared memory because each key vec is consumed once by one thread, unlike repeatedly shared `q_vecs`. Vec assignment again favors coalescing: neighboring threads read neighboring vecs, advancing to later vecs on inner iterations[^paged-attn].

## QK dot product

Pseudocode flow: load `q_vecs` once, then outer-loop over `k_ptr` positions and inner-loop filling `k_vecs`, followed by scaled `Qk_dot<>::dot`[^paged-attn]:

```cpp
q_vecs = ...
for ... {
    k_ptr = ...
    for ... {
        k_vecs[i] = ...
    }
    float qk = scale * Qk_dot<scalar_t, THREAD_GROUP_SIZE>::dot(q_vecs[thread_group_offset], k_vecs);
}
```

Although each thread only fetches part of a query/key token, `Qk_dot<>::dot` performs cross-thread-group reduction, so the returned `qk` is the full query–key dot product (e.g. all 128 elements when `HEAD_SIZE=128` and group size 2)[^paged-attn].

## Softmax

Softmax is the normalized `exp(qk - qk_max) / exp_sum` formulation over all `qk` for the query, reduced across the whole thread block[^paged-attn].

Shared-memory `logits` holds one entry per context token[^paged-attn]:

- Each thread group writes its assigned tokens' `qk` into `logits`, masking out `token_idx >= context_len`, and tracks a local `qk_max`[^paged-attn].
- Per-warp max is reduced with `VLLM_SHFL_XOR_SYNC` down to `THREAD_GROUP_SIZE`, stored to `red_smem[warp_idx]` by lane 0, then reduced across warps and broadcast to all threads[^paged-attn].
- Each thread converts its slice via `exp(logits[i] - qk_max)`, accumulates a local `exp_sum`, reduces it across the block with `block_sum`, then normalizes with `inv_sum = 1 / (exp_sum + 1e-6)`[^paged-attn].

The resulting `logits` array is the normalized attention weights consumed by the value stage[^paged-attn].

## Value path

Unlike query/key, values have no thread-group concept. One value block is viewed as `HEAD_SIZE` rows by `BLOCK_SIZE` columns split into `v_vecs`; each thread always fetches `V_VEC_SIZE` elements from the same head position across `V_VEC_SIZE` tokens[^paged-attn].

Outer iterations walk blocks (loading a `logits_vec` of `V_VEC_SIZE` weights); inner iterations walk head rows (loading a `v_vec` and accumulating `dot(logits_vec, v_vec)` into `accs[NUM_ROWS_PER_THREAD]`). Each `accs` entry therefore corresponds to head positions owned by that thread[^paged-attn].

Worked sizing from the source: `BLOCK_SIZE=16`, `V_VEC_SIZE=8`, `HEAD_SIZE=128`, `WARP_SIZE=32` gives `32*8=256` elements per warp per inner iteration and `128*16/256=8` inner iterations per value block; each thread accumulates 8 head positions (e.g. thread 0 accumulates positions 0, 32, ..., 224)[^paged-attn].

## LV reduction and output

- Within each warp, `accs` entries are reduced with `VLLM_SHFL_XOR_SYNC` over `NUM_V_VECS_PER_ROW` so each thread holds that block's accumulation for its head positions[^paged-attn].
- Across warps, upper warps spill `accs` to shared `out_smem` while lower warps add the spilled values back, iteratively halving until every thread holds the all-context accumulation for its head positions (distributed across thread registers)[^paged-attn].
- The destination is `out_ptr = out + seq_idx * num_heads * max_num_partitions * HEAD_SIZE + head_idx * max_num_partitions * HEAD_SIZE + partition_idx * HEAD_SIZE`; each thread writes its `NUM_ROWS_PER_THREAD` results with `from_float`, guarded by `row_idx < HEAD_SIZE` and `lane % NUM_V_VECS_PER_ROW == 0`[^paged-attn].

## Citation

The source cites the PagedAttention paper as[^paged-attn]:

- Kwon et al., *Efficient Memory Management for Large Language Model Serving with PagedAttention*, SOSP 2023.

## Coverage limits

- Referenced figures (`query.png`, `q_vecs.png`, `key.png`, `k_vecs.png`, `value.png`, `logits_vec.png`, `v_vec.png`) are absent from `raw/` and were not inspected; layout claims above rest on the design-doc prose and code sketches[^paged-attn].
- Index arithmetic, `Qk_dot` reduction internals, and the `??? code` LV snippet are explicitly incomplete or provisional in the source and should be verified against `csrc/attention/attention_kernels.cu` before reuse[^paged-attn].

## Relationships

- Uses [vLLM Hybrid KV Cache Manager](vllm-hybrid-kv-cache-manager.md) — both describe paged/blocked KV-cache organization; this kernel is the consumer-side attention computation over such blocks.

[^paged-attn]: Paged Attention — `../raw/vllm/design/paged_attention.md`.
