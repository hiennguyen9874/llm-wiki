---
type: Concept
title: PagedAttention for LLM Serving
description: Virtual-memory paging for KV cache enabling on-demand blocks, prefix sharing, and high-throughput vLLM serving.
tags: [paged-attention, kv-cache, vllm, serving]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-16T12:00:00Z }
sources:
  - id: paged-serving
    resource: ../raw/PagedAttention.md
    title: PagedAttention và vLLM trong phục vụ LLM
  - id: paged-paper
    resource: ../raw/arXiv-2309.06180v1/main.tex
    title: Efficient Memory Management for Large Language Model Serving with PagedAttention
  - id: paged-first-principles
    resource: ../raw/paged-attention-from-first-principles-a-view-inside-vllm/index.md
    title: "Paged Attention from First Principles: A View Inside vLLM"
---

PagedAttention applies OS virtual-memory paging to GPU KV cache: each sequence's cache is split into fixed-size logical blocks mapped through a block table to arbitrary physical blocks, allocated on demand and shareable across sequences, leaving attention mathematics unchanged while enabling larger, dynamic batches in vLLM[^paged-serving].

The original paper is Kwon et al., SOSP '23 (UC Berkeley, Stanford, UCSD; Kwon and Li equal contribution), introducing PagedAttention plus the vLLM engine with near-zero KV-cache waste and intra-/inter-request sharing[^paged-paper].

A first-principles walkthrough (Hamza's Blog, 2025-09-11) rebuilds the same result from training-versus-inference workloads through naive KV caching, OS paging, paged KV management, and the paged attention kernel, with appendixes on batching, speculative decoding, and quantization[^paged-first-principles].

## Problem: prefill, decode, and KV-cache size

A request has a parallel prefill phase over the prompt and a sequential decode phase generating one token at a time; decode reuses cached keys and values rather than recomputing history and is typically memory-bandwidth bound[^paged-serving].

Per-token cache size follows approximately `2 × L × H_kv × D_h × bytes`, or `2 × L × d_model × bytes` for classic multi-head attention where KV heads span the hidden size[^paged-serving].

The source's OPT-13B example gives about 800 KB per token, so a 2,048-token sequence needs about 1.6 GB for one request's cache; modern MQA/GQA with fewer KV heads reduces this, but long context plus concurrency still makes cache a bottleneck[^paged-serving].

The paper derives 800 KB as `2 × 5120 × 40 × 2 bytes FP16` (key/value × hidden size × layers × bytes) and notes GPU compute grows faster than capacity (A100→H100 FLOPS >2× while memory stays ≤80 GB), so memory becomes the tighter bound[^paged-paper].

The walkthrough gives the same sizing as `2×bytes×n_layers×B×n_heads×d_head×n_seq`, with a Llama-2-13B FP16 anchor of about 0.78125 MiB per token (40 layers, 40 heads, `d_head=128`) and about 3.125 GiB for a full 4,096-token window, scaling linearly with batch size at roughly 0.78125 MiB per token per added sequence[^paged-first-principles]. Its model table lists Llama-2-7B (32/32/128/4096), Llama-2-13B (40/40/128/5120), OPT-7B (32/32/128/4096), OPT-13B (40/40/128/5120), OPT-30B (48/56/128/7168), OPT-66B (64/72/128/9216), and OPT-175B (96/96/128/12288) as layers/heads/`d_head`/`d_model`[^paged-first-principles].

First-principles framing: training sees the full sequence (blog example `Coffee solves everything` with `[SOS]`/`[EOS]`) and computes all positions in parallel under the causal mask, so it is compute-bound; inference must emit one token at a time without future tokens, repeatedly loading weights and cache, so decode is memory-bound[^paged-first-principles]. Prefill over the N-token prompt is still parallel and compute-bound and yields the first token plus KV entries, while each decode step is serial; the walkthrough names time-to-first-token (TTFT, growing with prompt length), inter-token latency (ITL), total end-to-end latency (E2EL), and token-generation time as the serving metrics[^paged-first-principles]. Its naive-decode arithmetic is a 1,000-token prompt plus 100 output tokens costing well over 100,000 token computations without reuse versus about 1,100 with cache appends[^paged-first-principles].

As KV-shrink context the walkthrough taxonomizes Multi-Query Attention (one shared K/V across heads, smaller cache at some quality cost), Grouped-Query Attention (query-head groups share one K/V; Llama-2 example), Multi-head Latent Attention (learned low-dimensional latent K/V with projection cost; DeepSeek-V2 example), Grouped Tied Attention (tied KV per group, reported halved cache, halved traffic, doubled arithmetic intensity versus GQA at GQA-level quality), and Grouped Latent Attention (latent form optimized for parallel sharding and distributed inference)[^paged-first-principles].

## Traditional allocation waste

Pre-PagedAttention systems commonly reserved a large contiguous region per sequence for the expected or maximum output length, producing three wastes[^paged-serving]:

- **Reserved memory:** allocated but not yet used because output length is unknown, e.g. 200 live tokens holding a 2,048-token reservation.
- **Internal fragmentation:** allocator rounding, e.g. a 513-token need receiving a 1,024-token chunk.
- **External fragmentation:** enough total free memory but split into noncontiguous pieces that cannot satisfy a large contiguous request.

These wastes shrink feasible batch size, which matters because large batches are needed to utilize the GPU[^paged-serving].

In the paper's measurements only about 20.4%–38.2% of KV-cache memory holds live token states under prior schemes, motivating on-demand paging[^paged-paper].

The walkthrough makes external fragmentation concrete with a buddy-allocator-style example: start with 128 free bytes, allocate 32 bytes to request A (0–31) and 16 bytes to request B (64–79), then allocate 8 bytes to a 7-byte request C (32–39) leaving 1 byte of internal waste; total free space is then 72 bytes (40–47, 48–63, 80–95, 96–127) yet no single contiguous 64-byte block exists because 64–79 sits in the middle, so a 64-byte request fails[^paged-first-principles]. Reserved-but-unused future-token slots are the internal-fragmentation counterpart when each request pre-reserves its maximum length[^paged-first-principles].

## Core idea: logical blocks and block table

PagedAttention splits each sequence's KV cache into logical blocks of fixed token count, e.g. `B=16`, mapped to any physical GPU blocks via a per-sequence block table[^paged-serving]:

```text
Logical blocks:   [0] [1] [2]
                   |   |   |
Physical blocks:  [7] [1] [12]
```

The source's OS analogy is process to sequence, virtual pages to logical blocks, physical frames to GPU physical blocks, and page table to block table; a 35-token sequence with `B=16` uses logical blocks for tokens 0–15, 16–31, and 32–34[^paged-serving].

The walkthrough grounds the OS side as `MOV REG,1000` going through the MMU/page table when present and raising a page fault for the OS to fetch the missing page from slower storage, place it in a free frame, update the mapping, and retry; its numeric example is a 64 KB virtual space in 16×4 KB pages backed by 32 KB physical memory in 8×4 KB frames, e.g. virtual page 0 in frame 2 and page 2 in frame 6 while absent page 8 faults[^paged-first-principles].

Attention is expressed per block with `K_j` and `V_j` holding that block's keys and values; the kernel walks the block table instead of assuming contiguous `K`/`V`, so layout and access change while attention results do not[^paged-serving].

Paper form with block size `B`: `K_j=(k_(j-1)B+1,…,k_jB)`, `V_j=(v_(j-1)B+1,…,v_jB)`, `A_ij` the score row on block `j`, `o_i=Σ_j V_j A_ijᵀ` with denominator summed over `⌈i/B⌉` blocks; the kernel fetches each `K_j`/`V_j` via the block table (paper example: query "forth" attending to blocks such as "Four score and seven")[^paged-paper].

## On-demand allocation and waste bound

vLLM allocates only enough blocks for the prompt, appends new tokens into the last block's free slots during decode, and extends the block table with a fresh physical block only when the last block fills[^paged-serving].

Because all physical blocks share one size, external fragmentation is nearly eliminated and no maximum-length reservation is needed; residual internal waste is confined to the final block[^paged-serving].

With block size `B`, each sequence wastes at most `B-1` token slots, averaging about half a block under roughly uniform length distribution; the source calls this near-zero waste, not literally zero[^paged-serving].

Paper walkthrough (`B=4`, 7-token prompt): reserve only logical blocks 0–1 → physical 7 and 1, run prompt prefill with a conventional attention kernel, fill 4 + 3 slots leaving one free; first decode writes into the free slot and updates `#filled`; second decode allocates a fresh physical block (block 3) for the new logical block[^paged-paper]. Block tables therefore store physical-block IDs plus filled counts; GPU workers hold the physical blocks while the centralized scheduler holds the mapping[^paged-paper].

The walkthrough's vLLM operational view (adapted from Aleksa Gordic's post) is engine → processor (tokenization/request format) → scheduler → KV cache manager in the middle, with CPU-side indexing as a doubly linked global free-block pool plus per-request block tables bridging to equal-sized GPU KV blocks[^paged-first-principles]. At initialization the engine measures available VRAM, chooses token block size `B` (not batch), and sizes blocks as `2×B×num_kv_heads×head_size×bytes` for K plus V, so GQA/MQA with fewer KV heads fit more blocks in the same memory[^paged-first-principles]. Allocation is just-in-time per engine step: prefill with known N allocates `⌈N/B⌉` blocks, decode usually adds one token (more under speculative decoding) and takes a new block only when the last logical block would overflow, and finished requests return blocks to the pool where any equal-sized block can serve any future request[^paged-first-principles]. Its `B=4`, 7-token example pops two pool IDs into the block table (each entry tracking physical ID, reference count, and often block hash), shares identical-prefix blocks by refcount without copying, and treats blocks as read-shared but write-unique: a writer to shared state gets a fresh block via block-granularity copy-on-write[^paged-first-principles]. Residual internal waste is therefore bounded by at most `B−1` slots in the final block; larger `B` means fewer lookups but coarser reuse, smaller `B` means tighter packing but more lookups[^paged-first-principles]. Practical wins named are smoother continuous batching across mixed lengths, cheap multi-completion/beam prefix sharing diverging only on new tokens, and block-level pressure policy (pause new prefill, evict lower-priority requests by returning blocks, or recompute where acceptable)[^paged-first-principles].

## Attention over paged cache

At decode position `i`, the kernel iterates logical blocks, resolves each to its physical block, computes `Q · K_block` scores, maintains softmax state, and accumulates the weighted `V_block` sum[^paged-serving].

The implementation uses online softmax with running maximum, exponential sum, and accumulated output rather than materializing all scores, assigns warps to KV blocks, and lays out key/value caches for coalesced reads[^paged-serving].

The extra `logical block → block table → physical block` indirection requires specialized kernels fusing KV reshape/write, table lookup plus blocked attention, and copy-on-write operations[^paged-serving].

The walkthrough's kernel example uses query token *soon* whose history is scattered (e.g. one block holding `sing, calm, night, bring`, another holding `peace, soon`, another holding `Sun, sets, low, bid`) but traversed in logical order via the block table as `K_j=[k_(j−1)B+1,…,k_jB]`, `V_j=[v_(j−1)B+1,…,v_jB]`, with per-block scores `q_iᵀK_j/√d`, a running softmax normalizer (running maximum plus running sum streamed across blocks), and accumulation `o_i=Σ_j V_j A_ijᵀ` identical to contiguous attention[^paged-first-principles].

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

The walkthrough restates the same headline as prior systems wasting 60%–80% of KV-cache memory versus under 4% waste with vLLM and 2–3× higher throughput, illustrated with the paper's waste-comparison plot[^paged-first-principles].

## Limitations and evolution

Reported trade-offs are indirect table lookup, kernels that cannot assume contiguous K/V, block-size choice between fewer allocations and more internal waste versus more metadata and management overhead, copy cost when many sequences branch inside an unfilled block, small single-request-latency benefit, and no fix for attention's growth with context length[^paged-serving].

Paper discussion adds[^paged-paper]: paging is not universally useful — static-shape DNN training and compute-bound non-LLM serving may lose from indirection/noncontiguity; vLLM's LLM-specific twists are all-or-nothing swap, recomputation recovery (infeasible in OS), and fused access+compute kernels to hide indirection. Related-work positioning: Orca iteration-level scheduling is complementary (Orca interleaves requests; vLLM fits more requests in memory); vs FlexGen (swap without online serving), OLLA (no fine-grained online block management), and FlashAttention (tiling for compute/IO, not online block management)[^paged-paper].

The source also relays the current vLLM documentation warning that the original PagedAttention description is historical and no longer fully describes the modern implementation, which has evolved substantially since the 2023 system[^paged-serving].

The walkthrough's stated caveat is that paging helps because LLM serving needs dynamic allocation and is GPU-memory-capacity bound; it does not generally transfer to static-shape DNN training (allocatable ahead of time) or compute-bound non-LLM serving, where indirection plus non-contiguous access can hurt[^paged-first-principles]. Its appendix is a secondary survey rather than new PagedAttention evidence: static batching (fixed batch, first request waits for last; printer analogy; whole batch waits for slowest) versus Orca iteration-level continuous batching (per-iteration batch revision, finished sequences replaced in place; `continuous` preferred over `dynamic`; Anyscale 23× throughput/p50-latency pointer), speculative decoding (K tokens need K forwards, large models slower per step reading full weights; small draft proposes, large verifies in parallel accepting matches; easy-token plus memory-bound observations; speculative-execution/speculative-sampling/speculative-decoding staging with probabilistic acceptance preserving the target distribution; T5-XXL 2–3× lossless; Google Research blog plus illustration video), and quantization (Hunyuan-Large 389B/52B-active and DeepSeek-V3 671B/37B-active motivation, all parameters resident despite sparse activation, `Memory=Bits/8×Params` table from ~5,368 GB at 64-bit to ~335.5 GB at 4-bit for 671B, tensor/pipeline parallelism, affine scale/zero-point mapping with symmetric-versus-asymmetric and post-ReLU bucket-waste trade-offs, Lei Mao pointer)[^paged-first-principles]. For wiki reuse, prefer the dedicated [Speculative Decoding Foundations](speculative-decoding-foundations.md), [AI Inference, KV Cache, and Serving Optimizations](ai-inference-kv-cache-fundamentals.md), [KV Cache Compression and Optimization](kv-cache-compression-optimization.md), and quantization pages over this appendix summary.

## Relationships

- Uses [vLLM Paged Attention Kernel](vllm-paged-attention-kernel.md) — synthesis: historical CUDA-kernel walkthrough for the paged query/key/value paths, softmax reduction, and output writeback summarized above.
- Related to [AI Inference, KV Cache, and Serving Optimizations](ai-inference-kv-cache-fundamentals.md) — synthesis: prefill/decode, per-token sizing, and runtime-optimization context extended here into block tables, on-demand growth, and sharing mechanics.
- Related to [KV Cache Compression and Optimization](kv-cache-compression-optimization.md) — synthesis: paged cache as the system-level manage-placement pillar alongside quantization, eviction, prefix reuse, and offload.
- Related to [vLLM Prefix Caching](vllm-prefix-caching.md) — synthesis: hash-based full-block reuse and eviction policy building on the shared-physical-block mechanism above.
- Related to [vLLM Request Preemption](vllm-request-preemption.md) — synthesis: V1 recompute-preemption tuning and observability for the swap-versus-recompute choice above.
- Related to [Speculative Decoding Foundations](speculative-decoding-foundations.md) — synthesis: lossless draft-verify-accept proof and speedup math behind the walkthrough's speculative-decoding appendix summary above.
- Contrasts with [FlashAttention Exact IO-Aware Attention](flashattention.md) — synthesis: FlashAttention reorders exact attention into SRAM tiles to cut HBM traffic, while PagedAttention reorganizes cache layout to cut fragmentation and enable sharing.

## Coverage limits

- Vietnamese synthesis file read in full; no local attachments were referenced.
- Original paper `main.tex` plus `intro.tex`, `eval.tex`, `discussion.tex`, `related_work.tex`, and `conclusion.tex` read in full; `figures/*.pdf` and `main.bbl`/`reference.bib` not inspected, so figure pixels and full bibliography were not verified.
- Orca comparisons are paper-simulated variants assuming buddy allocation (Orca not public at the time), not direct Orca measurements; FasterTransformer uses the authors' custom dynamic-batch scheduler.
- All formulas, OPT-13B and 1.6 GB sizing, B=16 and 35-token mapping, waste bounds, pseudocode, OS table, Orca Max/Pow2/Oracle definitions, and 2–4× headline are source-reported and not independently verified.
- First-principles walkthrough `index.md` read in full; `assets/` (Excalidraw SVGs/WebP, `pgvisualfinal.gif`, `memshare.gif`, static/continuous batching WebP, `38am-1.webp` waste plot, TTFT/ITL diagrams) listed but not visually inspected, and the speculative-decoding illustration video plus outward links (Aleksa Gordic vLLM post, Anyscale continuous-batching post, Google Research speculative-decoding blog, Lei Mao quantization post, arXiv papers, vLLM/TensorRT-LLM/TGI repos) not followed, so visual-only and off-page evidence is not captured.
- All Llama-2-13B 0.78125 MiB/token and 3.125 GiB figures, model-table dimensions, Coffee/`[SOS]`/`[EOS]` training-parallelism framing, TTFT/ITL/E2EL growth claims, 100k-versus-1,100 caching arithmetic, MQA/GQA/MLA/GTA/GLA characterizations including GTA halving/doubling and GLA sharding claims, buddy-allocator byte walkthrough, MOV/MMUs and 64KB/32KB paging numbers, engine/free-pool/block-table/`⌈N/B⌉`/refcount/hash/read-shared-write-unique/`B−1` details, *soon* scattered-block example with running max/sum equivalence, <4% versus 60–80% and 2–3× restatement, non-transfer caveat, and static/continuous, speculative-execution/sampling/decoding, Hunyuan/DeepSeek memory-table, affine `s`/`z`, and symmetric/asymmetric appendix claims are source-reported from this explainer and not independently verified.
- Full affine quantization derivation and three-stage speculative-decoding theory were intentionally not duplicated here; they belong to dedicated quantization and speculative-decoding concepts where those pages are primary.
- No secrets, credentials, tokens, private keys, or PII were found in the source.

[^paged-serving]: PagedAttention và vLLM trong phục vụ LLM — `../raw/PagedAttention.md`, covering prefill/decode phases, KV-cache sizing and OPT-13B example, reserved/internal/external fragmentation, logical/physical blocks and block table with OS analogy, on-demand growth and near-zero-waste bound, blocked attention with online softmax and fused kernels, shared blocks with copy-on-write, continuous-batching synergy, swap versus recomputation preemption, O(n) non-goal, PagedAttention versus FlashAttention comparison, 2–4× vLLM results with Orca baselines, limitations, and historical-implementation caveat.
[^paged-first-principles]: Hamza El Shafie, "Paged Attention from First Principles: A View Inside vLLM" (Hamza's Blog, 2025-09-11) — `../raw/paged-attention-from-first-principles-a-view-inside-vllm/index.md`, covering training compute-bound versus inference memory-bound framing with transformer flow and Coffee/`[SOS]`/`[EOS]` example, prefill/TTFT versus decode/ITL/E2EL mechanics with 1,000+100 naive-versus-cached arithmetic, MQA/GQA/MLA/GTA/GLA taxonomy, Llama-2-13B 0.78125 MiB/token and 3.125 GiB sizing plus seven-model table, reserved/internal/external fragmentation with buddy-allocator walkthrough, MMU/`MOV REG,1000`/page-fault and 64KB/16-page versus 32KB/8-frame OS analogy, vLLM engine/scheduler/manager plus doubly linked free pool and block-table (`⌈N/B⌉`, overflow-check JIT, phys-ID/refcount/hash, read-shared-write-unique CoW, `B−1` bound, pressure policy) operational view, block-form attention with *soon* scattered-block example and running-softmax streaming, <4% versus 60–80% and 2–3× headline with waste plot, non-transfer caveat, and static/continuous batching plus speculative-decoding plus quantization appendixes.
[^paged-paper]: Kwon et al., Efficient Memory Management for Large Language Model Serving with PagedAttention (SOSP '23) — `../raw/arXiv-2309.06180v1/main.tex` plus `intro.tex`, `eval.tex`, `discussion.tex`, `related_work.tex`, `conclusion.tex`, covering SOSP identity and contributions, autoregressive/Transformer background and prefill/decode phases, three memory wastes and 800 KB/token derivation, block-wise attention `K_j`/`V_j`/`A_ij`, block tables and 7-token walkthrough, parallel/beam/shared-prefix/mixed decoding with refcounts and copy-on-write, `fork`/`append`/`free`, FCFS plus all-or-nothing plus sequence-group scheduling, swap vs recompute, Megatron-LM SPMD distributed map broadcast, FastAPI plus 8.5K/2K implementation with three fused kernels, OPT/LLaMA configs and ShareGPT/Alpaca/Poisson/normalized-latency method with simulated Orca Oracle/Pow2/Max and FasterTransformer baselines, basic/parallel/beam/prefix/chatbot numbers, kernel/block-size/swap-vs-recompute ablations, discussion limits, and Orca/FlexGen/OLLA/FlashAttention related work.
