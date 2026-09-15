---
type: Concept
title: PagedAttention for LLM Serving
description: Virtual-memory paging for KV cache enabling on-demand blocks, prefix sharing, and high-throughput vLLM serving.
tags: [paged-attention, kv-cache, vllm, serving]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T05:07:53Z }
sources:
  - id: paged-serving
    resource: ../raw/PagedAttention.md
    title: PagedAttention và vLLM trong phục vụ LLM
  - id: paged-paper
    resource: ../raw/arXiv-2309.06180v1/main.tex
    title: Efficient Memory Management for Large Language Model Serving with PagedAttention
---

PagedAttention applies OS virtual-memory paging to GPU KV cache: each sequence's cache is split into fixed-size logical blocks mapped through a block table to arbitrary physical blocks, allocated on demand and shareable across sequences, leaving attention mathematics unchanged while enabling larger, dynamic batches in vLLM[^paged-serving].

The original paper is Kwon et al., SOSP '23 (UC Berkeley, Stanford, UCSD; Kwon and Li equal contribution), introducing PagedAttention plus the vLLM engine with near-zero KV-cache waste and intra-/inter-request sharing[^paged-paper].

## Problem: prefill, decode, and KV-cache size

A request has a parallel prefill phase over the prompt and a sequential decode phase generating one token at a time; decode reuses cached keys and values rather than recomputing history and is typically memory-bandwidth bound[^paged-serving].

Per-token cache size follows approximately `2 × L × H_kv × D_h × bytes`, or `2 × L × d_model × bytes` for classic multi-head attention where KV heads span the hidden size[^paged-serving].

The source's OPT-13B example gives about 800 KB per token, so a 2,048-token sequence needs about 1.6 GB for one request's cache; modern MQA/GQA with fewer KV heads reduces this, but long context plus concurrency still makes cache a bottleneck[^paged-serving].

The paper derives 800 KB as `2 × 5120 × 40 × 2 bytes FP16` (key/value × hidden size × layers × bytes) and notes GPU compute grows faster than capacity (A100→H100 FLOPS >2× while memory stays ≤80 GB), so memory becomes the tighter bound[^paged-paper].

## Traditional allocation waste

Pre-PagedAttention systems commonly reserved a large contiguous region per sequence for the expected or maximum output length, producing three wastes[^paged-serving]:

- **Reserved memory:** allocated but not yet used because output length is unknown, e.g. 200 live tokens holding a 2,048-token reservation.
- **Internal fragmentation:** allocator rounding, e.g. a 513-token need receiving a 1,024-token chunk.
- **External fragmentation:** enough total free memory but split into noncontiguous pieces that cannot satisfy a large contiguous request.

These wastes shrink feasible batch size, which matters because large batches are needed to utilize the GPU[^paged-serving].

In the paper's measurements only about 20.4%–38.2% of KV-cache memory holds live token states under prior schemes, motivating on-demand paging[^paged-paper].

## Core idea: logical blocks and block table

PagedAttention splits each sequence's KV cache into logical blocks of fixed token count, e.g. `B=16`, mapped to any physical GPU blocks via a per-sequence block table[^paged-serving]:

```text
Logical blocks:   [0] [1] [2]
                   |   |   |
Physical blocks:  [7] [1] [12]
```

The source's OS analogy is process to sequence, virtual pages to logical blocks, physical frames to GPU physical blocks, and page table to block table; a 35-token sequence with `B=16` uses logical blocks for tokens 0–15, 16–31, and 32–34[^paged-serving].

Attention is expressed per block with `K_j` and `V_j` holding that block's keys and values; the kernel walks the block table instead of assuming contiguous `K`/`V`, so layout and access change while attention results do not[^paged-serving].

Paper form with block size `B`: `K_j=(k_(j-1)B+1,…,k_jB)`, `V_j=(v_(j-1)B+1,…,v_jB)`, `A_ij` the score row on block `j`, `o_i=Σ_j V_j A_ijᵀ` with denominator summed over `⌈i/B⌉` blocks; the kernel fetches each `K_j`/`V_j` via the block table (paper example: query "forth" attending to blocks such as "Four score and seven")[^paged-paper].

## On-demand allocation and waste bound

vLLM allocates only enough blocks for the prompt, appends new tokens into the last block's free slots during decode, and extends the block table with a fresh physical block only when the last block fills[^paged-serving].

Because all physical blocks share one size, external fragmentation is nearly eliminated and no maximum-length reservation is needed; residual internal waste is confined to the final block[^paged-serving].

With block size `B`, each sequence wastes at most `B-1` token slots, averaging about half a block under roughly uniform length distribution; the source calls this near-zero waste, not literally zero[^paged-serving].

Paper walkthrough (`B=4`, 7-token prompt): reserve only logical blocks 0–1 → physical 7 and 1, run prompt prefill with a conventional attention kernel, fill 4 + 3 slots leaving one free; first decode writes into the free slot and updates `#filled`; second decode allocates a fresh physical block (block 3) for the new logical block[^paged-paper]. Block tables therefore store physical-block IDs plus filled counts; GPU workers hold the physical blocks while the centralized scheduler holds the mapping[^paged-paper].

## Attention over paged cache

At decode position `i`, the kernel iterates logical blocks, resolves each to its physical block, computes `Q · K_block` scores, maintains softmax state, and accumulates the weighted `V_block` sum[^paged-serving].

The implementation uses online softmax with running maximum, exponential sum, and accumulated output rather than materializing all scores, assigns warps to KV blocks, and lays out key/value caches for coalesced reads[^paged-serving].

The extra `logical block → block table → physical block` indirection requires specialized kernels fusing KV reshape/write, table lookup plus blocked attention, and copy-on-write operations[^paged-serving].

## Sharing, decoding scenarios, and APIs

Sequences can point their logical blocks at the same physical blocks with a reference count, so parallel samples, beam-search candidates, or shared prefixes store the common prompt once[^paged-serving].

When a sequence must write a shared block, copy-on-write allocates a new physical block, copies the old contents, redirects that sequence, and decrements the old block's count; only divergent suffixes consume private memory[^paged-serving].

Paper specifics[^paged-paper]:

- **Parallel sampling:** prompt logical blocks map to one physical copy (paper example: logical 0–1 of both samples → physical 7 and 1, refcount 2); only the last logical block diverges via block-granularity copy-on-write.
- **Beam search:** width `k` keeps top-`k` of `k·|V|` expansions per step; sharing is dynamic like a process tree from compound forks (paper `k=4` example shares block 0 across all candidates, frees blocks 2, 4, 5, 8 after pruning, allocates 9–12 for survivors). This avoids the large KV copies prior systems paid when a survivor continues from another candidate's prefix; copy-on-write touches at most one block.
- **Shared prefix:** provider pre-reserves physical blocks for a system/few-shot prefix (OS shared-library analogy); user prompts map to those blocks copy-on-write and compute only the task suffix.
- **Mixed decoding:** one logical→physical mapping layer hides sharing patterns, so greedy, sampling, and beam requests with different sharing can batch together.
- **APIs:** vLLM implements `fork` (new sequence from existing), `append` (add token), and `free` (delete sequence) to compose these algorithms.

## Continuous-batching synergy

PagedAttention and continuous batching are distinct but complementary: continuous batching revises the batch every iteration by evicting finished sequences and admitting new ones instead of waiting for a whole static batch[^paged-serving].

Paging makes that practical because the scheduler only needs free physical blocks rather than a large contiguous region; the general vLLM loop is central scheduler, per-iteration sequence selection, block-manager allocate/free/swap, GPU execution with PagedAttention, and block-table updates[^paged-serving].

## Preemption, scheduling, and distributed execution

When GPU blocks run out under priority pressure, vLLM can preempt sequences via swapping KV blocks to CPU RAM and restoring them later, avoiding recompute at PCIe/NVLink plus CPU-RAM cost, or via recomputation that discards cache and rebuilds it with a prefill rerun, avoiding CPU storage at extra compute cost[^paged-serving].

The better choice depends on prompt length, transfer bandwidth, system load, and recompute cost[^paged-serving].

Paper scheduling policy[^paged-paper]:

- FCFS across requests for fairness/starvation-freedom; latest arrivals preempted first.
- All-or-nothing eviction per sequence (all blocks of a sequence together, since they are accessed together).
- Sequences of one request (e.g. beam candidates) gang-scheduled as a sequence group and preempted/resumed together.
- **Swapping:** evicted blocks go to CPU RAM via a CPU block allocator; swapped-out bytes never exceed GPU KV allocation; arrivals pause until preempted sequences resume.
- **Recomputation:** discarded cache is rebuilt by concatenating generated tokens onto the prompt and running one parallel prompt-phase pass — cheaper than the original sequential decode.

Distributed execution uses Megatron-LM-style tensor parallelism (SPMD, attention split on heads, all-reduce among workers)[^paged-paper]. One centralized KV manager holds the logical→physical map; the scheduler broadcasts input IDs plus block tables each iteration, workers read KV by table and return sampled tokens. Each worker stores only its head shard under the same block IDs, so no worker-level memory-manager sync is needed[^paged-paper].

## Implementation kernels

The paper's engine uses a FastAPI frontend extending the OpenAI API (per-request max length, beam width `k`), ~8.5K lines Python for scheduler/block manager plus ~2K lines C++/CUDA, PyTorch/Transformers executors for GPT/OPT/LLaMA, and NCCL for distributed execution[^paged-paper].

Three fused optimizations[^paged-paper]:

- Fused reshape plus block-write for new KV cache.
- Fused block-read plus attention (adapted FasterTransformer kernel): one warp per KV block for coalesced reads, plus variable-length batch support.
- Fused block-copy batching copy-on-write moves into one launch instead of many `cudaMemcpyAsync` calls.

## Non-goal: per-token complexity

PagedAttention does not change standard decode attention from `O(n)` per new token to `O(1)`; each new token still attends over all prior context and reads an `n`-growing cache[^paged-serving].

Its wins are allocation efficiency, fragmentation reduction, prefix sharing, larger concurrent batches, and flexible batch evolution — mainly system throughput rather than single-request latency[^paged-serving].

## PagedAttention versus FlashAttention

| PagedAttention | FlashAttention |
|---|---|
| Serving-time KV-cache management | Attention computation method |
| Allows noncontiguous cache | Tiles to cut HBM traffic and materialization |
| Cuts fragmentation and duplication | Cuts memory traffic and intermediates |
| Matters most for multi-request decode | Matters for training and prefill |
| Memory abstraction plus kernels | Mainly algorithm plus kernels |

The two compose: a serving engine can manage memory with paged blocks while computing with an optimized or FlashAttention-compatible kernel on that cache[^paged-serving].

## Reported experimental results

Paper setup: OPT 13B/66B/175B and LLaMA-13B on GCP A2 A100s; e.g. 13B on 1×40 GB (26 GB weights, 12 GB KV, ~15.7K token slots), 66B on 4×A100 (132 GB weights, 21 GB KV, ~9.7K slots), 175B on 8×80 GB (346 GB weights, 264 GB KV, ~60.1K slots)[^paged-paper]. Workloads synthesize ShareGPT (long, high-variance) and Alpaca (ShareGPT ~8.4× longer prompts and ~5.8× longer outputs on average) with Poisson arrivals; metric is normalized latency (mean end-to-end latency / output length); mostly 1-hour traces (15-minute for 175B)[^paged-paper].

Baselines are FasterTransformer with a custom max-batch dynamic scheduler, plus three paper-simulated Orca variants (Orca was not public; authors assume buddy allocation): Oracle with exact output-length knowledge (infeasible upper bound), Pow2 reserving up to 2× true length, and Max always reserving 2,048 tokens[^paged-paper].

Paper-reported outcomes (A100-era, not a guarantee for current engines)[^paged-paper]:

- **Basic sampling:** vLLM sustains ~1.7–2.7× higher request rate than Orca Oracle and ~2.7–8× than Orca Max at equal latency on ShareGPT; up to ~22× vs FasterTransformer without fine-grained scheduling; e.g. OPT-13B batches ~2.2× more concurrent requests than Oracle and ~4.3× than Max. Alpaca gap narrows on 175B where short sequences plus large KV headroom make the workload compute-bound.
- **Parallel sampling / beam search (Alpaca, OPT-13B):** sharing saves ~6.1–9.8% of blocks for parallel sampling and ~37.6–55.2% for beam search (ShareGPT: ~16.2–30.5% and ~44.3–66.3%); vLLM lead over Oracle grows from ~1.3× in basic sampling to ~2.3× at beam width 6.
- **Shared prefix (LLaMA-13B, WMT16 EN-DE):** ~1.67× vs Oracle with 1-shot prefix (~80 tokens), ~3.58× with 5-shot prefix (~341 tokens).
- **Chatbot (ShareGPT, 1024-token history + ≤1024 generation):** ~2× vs all three Orca variants; Orca variants converge because buddy allocation rounds long prompts similarly.
- **Ablations:** PagedAttention attention kernel is ~20–26% slower than optimized FasterTransformer attention (table lookup, branches, variable lengths), but end-to-end still wins; block size 16 is the default (16–128 best on ShareGPT; 16–32 on Alpaca, larger degrades when sequences shorter than a block); swapping beats recomputation at large blocks while recomputation wins at small blocks where many tiny PCIe transfers throttle swap, with comparable end-to-end at 16–64.

The earlier 2–4× headline remains a fair summary at equal latency, with larger gains for bigger models, longer sequences, multi-output sampling, wider beams, and highly variable lengths[^paged-serving].

## Limitations and evolution

Reported trade-offs are indirect table lookup, kernels that cannot assume contiguous K/V, block-size choice between fewer allocations and more internal waste versus more metadata and management overhead, copy cost when many sequences branch inside an unfilled block, small single-request-latency benefit, and no fix for attention's growth with context length[^paged-serving].

Paper discussion adds[^paged-paper]: paging is not universally useful — static-shape DNN training and compute-bound non-LLM serving may lose from indirection/noncontiguity; vLLM's LLM-specific twists are all-or-nothing swap, recomputation recovery (infeasible in OS), and fused access+compute kernels to hide indirection. Related-work positioning: Orca iteration-level scheduling is complementary (Orca interleaves requests; vLLM fits more requests in memory); vs FlexGen (swap without online serving), OLLA (no fine-grained online block management), and FlashAttention (tiling for compute/IO, not online block management)[^paged-paper].

The source also relays the current vLLM documentation warning that the original PagedAttention description is historical and no longer fully describes the modern implementation, which has evolved substantially since the 2023 system[^paged-serving].

## Relationships

- Uses [vLLM Paged Attention Kernel](vllm-paged-attention-kernel.md) — synthesis: historical CUDA-kernel walkthrough for the paged query/key/value paths, softmax reduction, and output writeback summarized above.
- Related to [AI Inference, KV Cache, and Serving Optimizations](ai-inference-kv-cache-fundamentals.md) — synthesis: prefill/decode, per-token sizing, and runtime-optimization context extended here into block tables, on-demand growth, and sharing mechanics.
- Related to [KV Cache Compression and Optimization](kv-cache-compression-optimization.md) — synthesis: paged cache as the system-level manage-placement pillar alongside quantization, eviction, prefix reuse, and offload.
- Related to [vLLM Prefix Caching](vllm-prefix-caching.md) — synthesis: hash-based full-block reuse and eviction policy building on the shared-physical-block mechanism above.
- Related to [vLLM Request Preemption](vllm-request-preemption.md) — synthesis: V1 recompute-preemption tuning and observability for the swap-versus-recompute choice above.
- Contrasts with [FlashAttention Exact IO-Aware Attention](flashattention.md) — synthesis: FlashAttention reorders exact attention into SRAM tiles to cut HBM traffic, while PagedAttention reorganizes cache layout to cut fragmentation and enable sharing.

## Coverage limits

- Vietnamese synthesis file read in full; no local attachments were referenced.
- Original paper `main.tex` plus `intro.tex`, `eval.tex`, `discussion.tex`, `related_work.tex`, and `conclusion.tex` read in full; `figures/*.pdf` and `main.bbl`/`reference.bib` not inspected, so figure pixels and full bibliography were not verified.
- Orca comparisons are paper-simulated variants assuming buddy allocation (Orca not public at the time), not direct Orca measurements; FasterTransformer uses the authors' custom dynamic-batch scheduler.
- All formulas, OPT-13B and 1.6 GB sizing, B=16 and 35-token mapping, waste bounds, pseudocode, OS table, Orca Max/Pow2/Oracle definitions, and 2–4× headline are source-reported and not independently verified.
- No secrets, credentials, tokens, private keys, or PII were found in the source.

[^paged-serving]: PagedAttention và vLLM trong phục vụ LLM — `../raw/PagedAttention.md`, covering prefill/decode phases, KV-cache sizing and OPT-13B example, reserved/internal/external fragmentation, logical/physical blocks and block table with OS analogy, on-demand growth and near-zero-waste bound, blocked attention with online softmax and fused kernels, shared blocks with copy-on-write, continuous-batching synergy, swap versus recomputation preemption, O(n) non-goal, PagedAttention versus FlashAttention comparison, 2–4× vLLM results with Orca baselines, limitations, and historical-implementation caveat.
[^paged-paper]: Kwon et al., Efficient Memory Management for Large Language Model Serving with PagedAttention (SOSP '23) — `../raw/arXiv-2309.06180v1/main.tex` plus `intro.tex`, `eval.tex`, `discussion.tex`, `related_work.tex`, `conclusion.tex`, covering SOSP identity and contributions, autoregressive/Transformer background and prefill/decode phases, three memory wastes and 800 KB/token derivation, block-wise attention `K_j`/`V_j`/`A_ij`, block tables and 7-token walkthrough, parallel/beam/shared-prefix/mixed decoding with refcounts and copy-on-write, `fork`/`append`/`free`, FCFS plus all-or-nothing plus sequence-group scheduling, swap vs recompute, Megatron-LM SPMD distributed map broadcast, FastAPI plus 8.5K/2K implementation with three fused kernels, OPT/LLaMA configs and ShareGPT/Alpaca/Poisson/normalized-latency method with simulated Orca Oracle/Pow2/Max and FasterTransformer baselines, basic/parallel/beam/prefix/chatbot numbers, kernel/block-size/swap-vs-recompute ablations, discussion limits, and Orca/FlexGen/OLLA/FlashAttention related work.
