---
type: Concept
title: SGLang Unified Radix Cache
description: One token-keyed radix topology with FULL, SWA, and MAMBA component reuse, native HiCache tiers, session-aware eviction, and an experimental Rust tree core.
tags: [sglang, radix-cache, prefix-caching, hybrid-attention, mamba, hicache, kv-cache]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:59:16Z }
sources:
  - id: unified-radix-cache
    resource: ../raw/2026-08-11-unified-radix-cache/index.md
    title: 'Unified Radix Cache: One Tree for Hybrid Model Prefix Caching'
  - id: qwen38-day0
    resource: ../raw/2026-08-12-qwen3-8-day0-support/index.md
    title: 'SGLang and Miles Add Day-0 Support for Qwen3.8'
  - id: qwen38-flash-next-day0
    resource: ../raw/2026-08-26-qwen-flash-next/index.md
    title: 'Qwen3.8-Flash-Next: Day-0 Support in SGLang'
---

SGLang Unified Radix Cache replaces a matrix of hybrid cache classes with one token-keyed radix topology plus composable reuse components, keeping FULL, sliding-window, and Mamba state under a shared prefix identity while HiCache, session hints, and a Rust tree core build on that identity[^unified-radix-cache].

## Why one tree

Prefix caching reuses KV when requests share the same token prefix. Under full attention, KV for a shared prefix stays valid as tokens append, so SGLang tracks token-sequence to KV-location mappings in a radix tree and returns the longest reusable prefix before prefill[^unified-radix-cache].

Hybrid models break that single rule. A request can combine full-attention KV, sliding-window KV, and recurrent state with different reuse boundaries: full KV is reusable across the whole matched prefix, sliding-window KV covers only the trailing window, and a recurrent state is valid only at an exact checkpoint. Forcing one boundary discards valid reuse or permits invalid reuse[^unified-radix-cache].

Encoding each combination as a specialized cache class creates a combinatorial class matrix, worse once orthogonal capabilities such as HiCache are added. Earlier implementations duplicated matching, insertion, locking, and eviction across variants[^unified-radix-cache].

[Unified Radix Cache](https://github.com/sgl-project/sglang/pull/21206) separates shared prefix identity from component-specific reuse validity. A single token-keyed radix topology provides the canonical coordinate for each prefix, while full-attention KV, sliding-window KV, and Mamba checkpoints attach as components. HiCache is native to the same component lifecycle across GPU L1, Host L2, and external L3. Auxiliary pools follow as sidecars without defining new reuse boundaries[^unified-radix-cache].

## Composable components

Hybrid cacheable values share the same token prefix but follow different reuse rules. The design maps the shared prefix to one topology and each reuse rule to a `TreeComponent`. `UnifiedTreeCore` runs common matching, splitting, insertion, locking, and eviction mechanics, while `UnifiedRadixCache` coordinates pool operations and each component defines only varying semantics[^unified-radix-cache].

- `FULL` is always present and provides path reuse: it keeps KV for every token in the matched prefix and protects the ancestor path[^unified-radix-cache].
- `SWA` provides window reuse: it requires a contiguous trailing window, while older SWA slots may be empty tombstones whose radix nodes remain in the shared topology[^unified-radix-cache].
- `MAMBA` provides checkpoint reuse: it requires one recurrent checkpoint at the reusable frontier and copies shared state into a private request slot before mutation[^unified-radix-cache].

Model compositions on the same tree[^unified-radix-cache]:

- DeepSeek-V4: `FULL` plus `SWA`.
- Kimi-K3: `FULL` plus `MAMBA` for its KDA recurrent state.
- Qwen3.8-2.4T-A95B: `FULL` plus `MAMBA`, where each GDN checkpoint bundles recurrent state plus convolution windows with copy-on-write into a private slot before mutation and new checkpoints at prefill chunk boundaries and decode intervals[^qwen38-day0].
- Qwen3.8-Flash-Next: GDN plus QSA KV management compatible with Radix Cache — original K/V stays in the normal paged pool while QSA adds one BF16 compressed index key per four tokens, with page-aligned `full_slot / 4` addressing letting the compressed cache follow Radix Cache ownership without a separate lifecycle[^qwen38-flash-next-day0].
- Inkling: `FULL` plus `SWA` plus `MAMBA`.

A new family reuses an existing composition, or adds a new `TreeComponent` when its reuse rule cannot be expressed — without another tree implementation[^unified-radix-cache].

## Finding a safe reuse boundary

During prefix matching, `UnifiedTreeCore` follows the canonical `FULL` path and treats each visited node as a candidate boundary. A `FULL` match alone is insufficient: every active component creates a validator and the reusable boundary advances only when all validators accept the candidate. Rejection does not stop traversal because a later node may still pass[^unified-radix-cache].

In the source example, the walk reaches `n4` but `n1` and `n2` pass every validator while `n3` and `n4` fail at least one check, so `n2` remains the deepest safe result[^unified-radix-cache].

After traversal the core builds a `MatchResult`. Component finalizers then prepare selected values for reuse, including the copy needed when a shared Mamba checkpoint becomes private to one request[^unified-radix-cache].

## Component hooks across the lifecycle

| Lifecycle | What the component decides |
| --- | --- |
| Match | `create_match_validator` determines whether a candidate is reusable. `finalize_match_result_in_tree_core` and `finalize_match_result_in_cache` prepare the selected result. |
| Split | `redistribute_on_node_split` determines how component data moves when a radix node is divided. |
| Insert | `update_component_on_insert_overlap` and `commit_insert_component_data` determine which pool indices the component owns and where new data attaches. |
| Lock | `acquire_component_lock` and `release_component_lock` protect a path, a trailing window, or one checkpoint. |
| Evict | `evict_device_start`, `evict_device_next_node`, and `evict_device_end` select device candidates. `evict_component` removes component data, and `drive_host_eviction` reclaims host resources. |

This contract keeps the tree core generic while preserving different correctness rules. Removing one component payload does not always remove the radix node: the remaining topology can still anchor other components, and the empty slot can remain as a tombstone until restored or the node becomes unnecessary[^unified-radix-cache].

## Native HiCache across tiers

Components determine what can be reused; HiCache determines where the payload resides. Unified Radix Cache carries the same component identity across GPU L1, Host L2, and an external L3 tier, so tier movement does not change prefix identity or reuse rule. Components describe required transfers and `HybridCacheController` executes the physical I/O[^unified-radix-cache].

### Anchors and sidecars

Not every physical pool needs its own component. An anchor determines reuse semantics or supplies page indices that other pools follow. A sidecar stores a separate payload but reuses the indices of its declared source pool and moves with that source without voting on the boundary or adding another radix slot[^unified-radix-cache].

DeepSeek-V4 makes this concrete. `FULL` covers the logical prefix while `SWA` covers only its trailing window, so both are components with independent device index spaces. In the normalized six-page example, the allocator maps `FULL` tail slots `F4, F5` to `SWA` slots `S0, S1` at runtime. The C4 and C128 compressed KV pools, indexer buffers, and compressor states do not define new reuse boundaries and register as sidecars — three pools following `FULL` and two following `SWA`[^unified-radix-cache].

### Multi-turn benchmark results

Multi-turn workloads grow a reusable conversational prefix each round. If lower tiers preserve that prefix after GPU exhaustion, hit rate should stay high and TTFT should grow more slowly[^unified-radix-cache].

Compared configurations: GPU L1 only, L1 plus Host L2, and L1 plus L2 plus a 500 GiB Mooncake Store distributed tier as L3. DeepSeek-V4-Flash uses `FULL` and `SWA` on 4xH200 TP4 with 48 clients, 60 rounds, 4,096 input plus 16 output tokens per turn. Inkling-Small uses `FULL`, `SWA`, and `MAMBA` on 8xH200 TP8 with 64 clients, 30 rounds, 1,216 input plus 64 output tokens per turn. Server commands use `SGLANG_ENABLE_UNIFIED_RADIX_TREE=1`, `--page-size 64`, `--hicache-ratio 2`, `--hicache-size 0`, `--hicache-mem-layout page_first`, `--hicache-io-backend kernel`, `--hicache-write-policy write_through`, and `--hicache-storage-prefetch-policy wait_complete`, with Mooncake flags for L3 and `benchmark/hicache/bench_multiturn.py` workload flags. Commands contain placeholders for model paths and Mooncake client config and are outlines, not a complete reproducible environment[^unified-radix-cache].

Per-round hit rate is the sum of cached prefix tokens across requests divided by the sum of complete prompt lengths. In both workloads L1 loses reusable prefixes first, L2 delays the limit, and L3 stays high after warmup and finishes above 96%. The two rows use different models, GPU counts, request shapes, and scales, so tiers compare only within each row[^unified-radix-cache].

- DeepSeek-V4-Flash L3: hit rate near 98%, average TTFT below 9 seconds, 145.5K effective input tokens/s versus 9.4K for L1 and 14.3K for L1 plus L2[^unified-radix-cache].
- Inkling-Small L3: 96.8% final hit rate, 1.23-second TTFT, 67.1K effective input tokens/s versus 15.5K for L1 and 21.1K for L1 plus L2[^unified-radix-cache].

Effective input-token throughput follows `bench_multiturn.py`: sum of complete prompt lengths divided by wall-clock duration. It credits cache-hit prefix tokens, so it measures serving progress under reuse rather than raw prefill compute; the L3 gain comes primarily from keeping reusable prefixes available after smaller tiers reach capacity[^unified-radix-cache].

## Session-aware eviction

[Session-aware eviction](https://github.com/sgl-project/sglang/pull/29173) is implemented directly in `UnifiedRadixCache`. Ordinary LRU records recent access but not which prefixes belong to active sessions and are likely reused next turn, so under pressure it can evict an active session GPU KV while retaining unrelated entries[^unified-radix-cache].

Applications attach a stable `session_id` to every request. After successful completion, the cache registers the reusable region for that session: `FULL` tracks its prefix path, `SWA` its trailing window, and `MAMBA` its reusable frontier. All sessions still share one topology and every turn still supplies its complete prompt[^unified-radix-cache].

These references change eviction order rather than pinning memory. `FULL` orders candidates by whether they are referenced, their session reference count, and the configured base priority. `SWA` and `MAMBA` first scan unreferenced entries in their own reusable regions, then fall back to referenced entries when more space is needed. The current policy covers GPU L1 and Host L2, not external L3[^unified-radix-cache].

When an application calls `/close_session`, the cache removes that session references without immediately deleting entries. Session generations and bounded closed-session tombstones prevent stale requests finishing after close or reopen from restoring released references[^unified-radix-cache].

### SWE-bench workload results

Evaluated on DeepSeek-V4-Pro and Qwen3.5-397B-A17B with TP8 and HiCache on SWE-bench agent trajectories. The baseline uses ordinary HiRadixCache with LRU; the comparison enables Unified Radix Cache plus `--enable-session-radix-cache`. Because this changes both implementation and eviction policy, observed differences are not an isolated ablation of session awareness[^unified-radix-cache].

At batch size 128, DeepSeek-V4-Pro device hit ratio rises from about 42% to 51%. At batch size 32, Qwen3.5-397B-A17B rises from about 5% to 34%. At batch size 64, Qwen total device plus host hit ratio rises from about 58% to 67%[^unified-radix-cache].

Corresponding TTFT is 11.0% and 2.9% lower for DeepSeek-V4-Pro at batch sizes 128 and 256, and 13.5% and 16.6% lower for Qwen3.5-397B-A17B at batch sizes 32 and 64, relative to the ordinary HiRadixCache baseline[^unified-radix-cache].

## Toward a Rust tree core

As a shared prefix grows, traversal, lock bookkeeping, LRU updates, and eviction scans add work to the scheduler critical path. `UnifiedRadixCache` separates this tree state machine from cache orchestration, making the core a natural native target[^unified-radix-cache].

The [experimental Rust Unified Radix Cache](https://github.com/sgl-project/sglang/pull/29074) is an opt-in L1-only prototype. Rust owns the radix topology, per-component lock accounting, intrusive LRU lists, and eviction walks. Python remains the single owner of request-to-token mappings and physical KV allocation. After mutating the tree, Rust returns deferred actions for Python to apply to pools. The prototype supports `FULL`, `SWA`, and `MAMBA`, but not HiCache[^unified-radix-cache].

Compared over a 200-turn synthetic conversation adding 100 input and generating 100 output tokens per turn, with the same model, flags, GPUs, and six trials: full attention with Qwen3-32B at TP2, SWA with gpt-oss-20b at TP2, and hybrid SSM with Qwen3-Next-80B-A3B at TP4. Reproduction scripts require a release build of the Rust extension[^unified-radix-cache].

- SWA workload: 38% lower TTFT across all 200 turns and 42% lower over turns 176 to 200[^unified-radix-cache].
- Full attention: 10% lower overall and 18% lower over the final 25 turns[^unified-radix-cache].
- Hybrid SSM: 5% lower overall and 7% lower over the final 25 turns[^unified-radix-cache].

The source subtracts the CUDA-event-timed GPU prefill interval from total TTFT. That residual includes tree bookkeeping, scheduling, synchronization, sampling, detokenization, transport, and other uninstrumented work — not a direct CPU timer — so the full Rust versus Python difference cannot be attributed only to radix operations. The hybrid SSM result illustrates the boundary: its residual falls substantially but the larger GPU forward limits visible total TTFT change[^unified-radix-cache].

The follow-up Rust `UnifiedTreeCoreInterface` RFC [#32710](https://github.com/sgl-project/sglang/pull/32710) defines the target ownership boundary with orchestration and pool management in Python behind a replaceable core. It currently supports `FULL` only and publishes no performance results[^unified-radix-cache].

## Future work

- Complete the replaceable Rust core tracked in roadmap [#20415](https://github.com/sgl-project/sglang/issues/20415): extend Rust to `SWA`, `MAMBA`, and HiCache while keeping pool allocation and orchestration in Python[^unified-radix-cache].
- Connect GPU L1 directly to external L3 tiers, making Host L2 an optional staging tier and exposing distributed memory as a larger shared cache through coordinated admission, prefetch, transfer, and eviction[^unified-radix-cache].
- Coordinate agentic KV caching across the serving stack per roadmap [#21846](https://github.com/sgl-project/sglang/issues/21846): extend the same cache identity across routers, prefill and decode workers, and HiCache to coordinate prefetch, demotion, and retention for sessions, subagents, and tool calls[^unified-radix-cache].

## Relationships

- Uses [SGLang HiCache System Design](sglang-hicache-design.md) for the L1/L2/L3 hierarchy, local-match / prefetch / write-back workflow, and storage-interface context that Unified components extend.
- Uses [SGLang HiCache Best Practices](sglang-hicache-best-practices.md) for layout, prefetch-policy, and Mooncake deployment flags reused in the multi-turn L3 setup.
- Uses [SGLang HiCache Runtime Storage Attach/Detach](sglang-hicache-runtime-attach-detach.md) for runtime L3 attach/detach mechanics complementary to Unified tier identity.
- Related to [SGLang DeepSeek-V4 Inference](sglang-deepseek-v4-inference.md) — DeepSeek-V4 `FULL` plus `SWA` composition plus C4/C128 sidecars is the Unified view of the ShadowRadix hybrid layout there.
- Related to [SGLang Qwen3.8 Inference](sglang-qwen3.8-inference.md) — Qwen3.8 `FULL` plus `MAMBA` GDN-checkpoint composition with copy-on-write and chunk-boundary checkpointing.
- Related to [SGLang Qwen3.8-Flash-Next Inference](sglang-qwen3.8-flash-next-inference.md) — GDN plus QSA KV management with paged original K/V and page-aligned compressed-index ownership following Radix Cache.
- Related to [SGLang HiSparse Hierarchical Sparse-Attention Memory](sglang-hisparse.md) — C4 offload hierarchy operating alongside Unified prefix identity on DeepSeek-V4.
- Depends on [SGLang Attention Backends](sglang-attention-backends.md) for the hybrid SWA execution context underlying window reuse.
- Related to [vLLM Hybrid KV Cache Manager](vllm-hybrid-kv-cache-manager.md) — alternative full plus efficient-attention intersection approach to hybrid prefix reuse.
- Related to [vLLM Prefix Caching](vllm-prefix-caching.md) for full-block reuse and eviction contrast with component voting and session-aware ordering.
- Related to [SGLang DeepSeek-V4.1 Inference](sglang-deepseek-v41-inference.md) — encoder-side SWA bounded replay rebuilds window KV from the final 128 cached tokens instead of requiring a stored window checkpoint.

## Coverage limits

- Source SVG diagrams for shared topology, component voting, DeepSeek-V4 sidecars, and session eviction were inspected as text; PNG benchmark charts for multi-turn TTFT/hit-rate, Rust TTFT, and SWE-bench hit/TTFT were taken from prose and captions without pixel-level verification[^unified-radix-cache].
- Server launch and `bench_multiturn.py` commands contain placeholders and were compiled as outlines, not verified as reproducible environments[^unified-radix-cache].
- Linked PRs, RFC, roadmaps, reproduction scripts, and benchmark records were not inspected beyond the identifiers and claims cited above[^unified-radix-cache].

[^unified-radix-cache]: Unified Radix Cache: One Tree for Hybrid Model Prefix Caching — `../raw/2026-08-11-unified-radix-cache/index.md`, covering one-tree component design, match/lifecycle hooks, HiCache anchors and sidecars, multi-turn and SWE-bench benchmarks, session-aware eviction, Rust prototype, and future work.
[^qwen38-day0]: SGLang and Miles Add Day-0 Support for Qwen3.8 — `../raw/2026-08-12-qwen3-8-day0-support/index.md`, covering Qwen3.8 `FULL` plus `MAMBA` GDN-checkpoint composition with copy-on-write and chunk-boundary checkpointing.
[^qwen38-flash-next-day0]: Qwen3.8-Flash-Next: Day-0 Support in SGLang — `../raw/2026-08-26-qwen-flash-next/index.md`, covering GDN plus QSA KV management with paged original K/V and page-aligned compressed-index Radix ownership.
