---
type: Concept
title: Kimi K3 Systems and Infrastructure
description: KDA co-design, MoonEP balanced MoE training, 1M-token RL infra, AgentENV sandboxes, and hybrid-cache serving for 2.8T Kimi K3.
tags: [kimi-k3, systems, infrastructure, kimi-delta-attention, context-parallelism, moonep, expert-parallelism, activation-memory, rl-infrastructure, agentenv, inference, prefix-cache]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: k3-infra
    resource: ../raw/arXiv-2607.24653v1/5-infrastructure.tex
    title: Kimi K3 Technical Report — infrastructure
---

Co-designed stack addresses three combined challenges rarely in one model: hybrid KDA attention, 3T-class sparse multimodal training/inference, and million-token agentic workloads, spanning architecture kernels, pretraining efficiency, long-context RL state, and production serving[^k3-infra].

## Algorithm-system co-design for KDA

KDA replaces growing softmax KV cache with fixed-size recurrent state `S in R^{d_k x d_v}`; serial update complicates parallelism but fixed size is cheap to transfer and reuse[^k3-infra].

### Kernels across regimes

- Chunkwise training/prefill kernel FlashKDA (CUTLASS) overlaps intra-chunk compute with cross-chunk state propagation, splitting token-parallel stages and head-parallel recurrence independently tuned, substantially over Triton reference; serves training plus prefill as flash-linear-attention backend[^k3-infra].
- Intra-device context parallelism for long prefill: TP alone leaves SMs idle on ultra-long sequences with few heads per rank; segment transitions computable independently of incoming state then composed exactly; SM-level auto CP planner partitions sequence across SMs of one rank with no cross-device communication (distinct from cross-device KCP)[^k3-infra].

### KDA Context Parallelism

Softmax CP exchanges KV blocks growing with length; linear attention carries fixed-size state. Prior linear CP sums zero-initialized local states, insufficient for KDA because update `S_t = M_t S_{t-1} + beta_t k_t v_t^T` with `M_t=(I-beta_t k_t k_t^T)Diag(alpha_t)` applies token-dependent transition to incoming state[^k3-infra].

- KCP decomposes each segment into locally computable cumulative transition `M^{t<-1}` and zero-start state `~S`; arbitrary entering state composes as `S = ~S + M * S_prev`, expanded over preceding ranks; rank-level updates are associative so incoming states recovered by prefix scan[^k3-infra].
- Each rank computes both fragments locally, exchanges via one fixed-size `all-gather`, then reconstructs in document order via `S <- M_j S + ~S_j`; linear compute scaling; builds on DeltaNet CP, implementation in FLA PR #691[^k3-infra].

## 3T-class pre-training infra

Base strategy combines pipeline parallelism with virtual stages, expert parallelism, ZeRO-1 data parallelism, Pipeline ZeRO-2 gradient sharding, and context parallelism; shared experts replicated across EP ranks; expert dispatch/combine all-to-all overlapped with compute[^k3-infra].

Three problems at 3T native multimodal scale: EP token imbalance, activations/gradients/optimizer exceeding memory, variable vision-encoder compute on critical path[^k3-infra].

### MoonEP balanced expert-parallel training

Conventional EP suffers imbalanced token loads (throughput loss) and dynamic shapes (memory fragmentation); MoonEP adds online planning and migration of redundant experts while preserving DeepEP-like flow; forward plans redundant experts from current micro-batch/layer router outputs and prefetches before routed compute; backward stages gradients in local reduce buffer then reduces to home ranks[^k3-infra].

- Perfect balance requires every rank receive exactly `S*K` tokens; at most `E/R` redundant experts per rank always suffices and bound is essentially tight (proof by filling underloaded from overloaded ranks in at most `R-1` fills with single-source remotes; tightness example with rank 0 empty needs `ceil(E(R-1)/R^2)`); reserving `E/R` slots guarantees feasibility unlike ECHO/UltraEP caps that can stall and need tuning while leaving imbalance[^k3-infra].
- Online planning uses GPU kernel near-optimal with negligible overhead versus offline ILP references, always respecting `E/R` bound[^k3-infra].
- Zero-copy communication: planning kernel precomputes every token destination, sends directly to expert-grouped remote positions, returns buffer views directly to compute; worst-case buffer `S*K` versus DeepEP `S*K*R`[^k3-infra].
- Sync-free static shapes eliminate per-layer MoE host-device sync and reduce launch overhead[^k3-infra].
- Workload-aware routed-expert GEMM scheduler adapts parameters to current token distribution via analytical hardware cost model plus offline autotuned coefficients; shared-expert GEMMs on separate stream overlapped with other kernels[^k3-infra].
- MoonEP open at `https://github.com/MoonshotAI/MoonEP`[^k3-infra].

### Memory-efficient training

- Unified activation manager: every saved tensor gets pluggable storage backend; recomputation, quantization, offload/remote-offload are composable per-tensor policies declared by annotations decoupled from model code; function-granularity recomputation supports cross-layer; single memory pool on main compute stream avoids multi-stream fragmentation/host overhead; layer-granularity prefetch overlapped; K3 uses mostly block-wise FP8 quantization plus offload/remote-offload with element-wise recomputation[^k3-infra].
- Memory-efficient MoE: rewrite permuted-probs gradient to depend on `act_output` plus upstream `doutput` not forward `output` (SonicMoE-inspired) at cost of light element-wise compute; forward group-GEMM saves only dispatch input, recomputes it in backward with communication overlapped with group-GEMM backward[^k3-infra].
- Memory-efficient AttnRes: block representation generated once at boundary and shared on GPU; AttnRes wrapped in checkpointing so per-layer saved activation matches standard residual; cache-based pipeline communication transfers only newly generated blocks incrementally and releases after micro-batch, reaching lower bound[^k3-infra].
- Balance activations across PP: interleaved 1F1B leaves more resident activations on early ranks; remotely offload to other PP ranks via Mooncake Transfer Engine[^k3-infra].
- Pipeline ZeRO-2 gradient sharding across DP with CPU-resident shards plus double GPU grad buffer; reduce into buffer then accumulate to CPU[^k3-infra].
- P2P Muon orthogonalization: instead of all-gathering full parameters on every rank, each rank P2P-fetches only shards it owns, eliminating full buffer and cutting memory plus volume; pipelined at model-chunk granularity to hide comms[^k3-infra].

### Multimodal encoder optimization

- Dynamic CP: partition single large image along patch dim across devices with gather-KV attention; divide CP group into load-balanced sub-CP groups for multiple large images so communication fraction does not grow with scale; remaining encoder work hidden in pipeline bubbles[^k3-infra].
- Encoder in PP bubbles: extends Kimi 2.5 Decoupled Encoder Process by further decomposing ViT: first micro-batch forwards run synchronously upfront, remaining forwards scheduled into bubbles, backwards analogously, largely eliminating effective vision overhead[^k3-infra].

## 1M agentic RL infra

Co-located RL keeps each 1M-context K3 experiment within few hundred GPUs; partial rollouts cut ultra-long tail latency but create rollout-KV versus training-memory contention[^k3-infra].

- External KV pool: 1M multi-step rollout makes prefix miss extremely expensive; partial-rollout restarts plus speculative-decoding churn worsen preemption/hit rate; write-back design keeps active decode blocks on GPU, writes reusable idle prefixes to CPU DRAM only on GPU eviction, prefetches before reuse; KDA states offloaded/prefetched with MLA blocks aligned; avoids redundant copies of still-resident blocks unlike write-through; DRAM provisioned by NVMe-offloading training weights/optimizer after train iteration, pool released after rollout to avoid contention[^k3-infra].
- Rollout auto-throttling scheduler: fixed concurrency from full-trajectory average is hard to estimate and conservative early, while too-high concurrency causes late-stage preemption; runtime signals (active/queued counts, KV utilization) dynamically control requests sent to engine, keeping early rollout utilized while throttling under pressure without manual tuning[^k3-infra].
- Gradient-buffer reuse for non-policy forwards: reference models too large to keep resident are kept on CPU and materialized chunk-by-chunk into policy FP32 gradient-buffer slots (safe because overwritten when real grads computed); with ZeRO-2 each GPU keeps two VPP-chunk buffers, one computes while other prefetches, hiding copy without extra memory[^k3-infra].

### AgentENV sandboxes

Multiple runtimes include container, GPU, and new microVM AgentENV (`https://github.com/kvcache-ai/AgentENV`) built for agentic AI around isolation, flexible lifecycles, and density[^k3-infra]:

- High-fidelity isolation via Firecracker microVMs tolerates aggressive exploration and reward-hacking attempts that caused kernel panics/deadlocks on containers, while permitting mounts, containers, even VMs for realism[^k3-infra].
- Flexible lifecycles on incremental checkpoint/resume (dirty pages only, 133ms checkpoint / 49ms resume): pause/resume frees memory/CPU while waiting for inference (up to 98% of sandbox lifetime), fork clones exact state for side-effect-free judging, snapshot at intervals for recovery[^k3-infra].
- High efficiency/density via OverlayBD plus custom ublk plus storage sharing plus P2P for sub-second launch of tens of thousands of unique-image sandboxes, plus COW memory and page-cache optimizations for up to 6.5x overcommit[^k3-infra].
- Totals: 51,219,741 sandboxes across 1,505,678 images during K3 training/evaluation[^k3-infra].

## Inference and serving

Hybrid KDA-MLA maintains two fundamentally different caches jointly at million-token scale; new modules plus extreme expert sparsity need tailored kernels; production mixes per-request costs spanning three orders of magnitude[^k3-infra].

### KDA-aware prefix cache

Prefix reusable only when KDA state and MLA KV both restorable at same boundary[^k3-infra].

- Unified layout packs fixed-size per-request KDA states into same paged block pool as per-token paged MLA KV with unified byte-size pages sharing alloc/refcount/evict; within page heads stored contiguously as minimal cross-node transfer unit; TP-degree mismatch handled by relayout on transfer path with zero GPU reshuffle; type-confused access yields garbage not plausible data as zero-overhead sanity check[^k3-infra].
- Decoupled granularities solve coarse-block problem (single shared block 1024-6144 forced by sparse KDA snapshots makes caching useless for shorter requests and chunked prefill): prefix hashing runs on fine hash blocks (e.g. 512) inside MLA pages while physical block stays coarse; KDA checkpoints saved only at sparse subset of MLA hash endpoints (typically conversation-turn boundaries); partial MLA pages registered under chained hash advancing as page fills; superseded intermediate KDA checkpoints recycled; checkpoints read-only snapshots restored by copy to private running state[^k3-infra].
- Lookup is two-stage: MLA matches whole physical blocks then hash endpoints inside first missing block (partial pages hittable); KDA requires checkpoint in every KDA cache group; hit is longest boundary satisfying both, always hash-multiple not necessarily physical-multiple (e.g. 2800-token match hits B=2560=5x512 inside 6144 block, zero recompute of [0,B))[^k3-infra].
- Consistency under concurrency: pin hit blocks across all groups before allocation (prevent eviction by private copy); exclude blocks allocated/registered in current step until copies land (prevent stale-byte reads); evicting one group's checkpoint atomically invalidates siblings (all-or-none hittability)[^k3-infra].

### High-performance kernels

- KDA decoding: bottleneck shifts to in-place recurrent-state management; MTP speculative verification rollback would multiply state traffic at large batches if snapshotting per draft position; cache only far-smaller projected inputs, rebuild accepted states on-chip, write back verified plus bonus tokens (concurrent ReplaySSM); single fused kernel covers short conv, norm, gating, recurrence, output norm over replay plus bonus plus next draft window; verification latency sublinear and below state-caching baselines; projection caches stay in decode stage so prefix cache and disaggregation payloads match non-speculative serving[^k3-infra].
- Block AttnRes two-phase (batched inter-block cached reads once per block plus per-layer intra-block online-softmax merge) optimized for memory: prefill uses sequence parallelism (TP all-reduce split to reduce-scatter plus all-gather with intra-block kernel between) so block reps materialized on exactly one rank; decoding overlaps inter-block kernel on side stream and fuses intra-block merge plus RMSNorm into preceding TP all-reduce, eliminating dedicated kernel[^k3-infra].
- Stable LatentMoE: fuse latent down-projection with router into single GEMM; shard latent weights and fuse output all-gather into GEMM epilogue via multimem stores, overlapped with shared-expert compute; routed-expert decode uses WarpDecode token-centric design (warp per output neuron streaming weights) subdivided into lane teams over experts plus warp reduce, with offline-permuted layout cutting dequant overhead, suited to small-batch memory-bound streaming where tile-centric kernels falter[^k3-infra].

### Fleet scheduling

- Cache-aware affinity: typical coding input carries 400K prefix but 4K increment, so hit avoids orders-of-magnitude re-prefill; route to cluster holding prefix cache (inter-cluster transfer far slower than intra-cluster fabric); consistent hashing pins each session to primary plus pre-assigned secondary for bounded failover (secondary holds no cache and re-prefills on failure, work spread uniformly)[^k3-infra].
- Budget-based admission: <2K short versus up to 1M ultra-long requests make average-request capacity/queueing/rate-limiting break and long bursts starve short TTFT; separate resource budgets per request class isolate bursty long-context traffic from system SLOs[^k3-infra].

## Relationships

- Depends on [Kimi K3 Architecture and Pre-training](kimi-k3-architecture-pretraining.md) — KDA recurrence, Block AttnRes, and LatentMoE structures optimized here.
- Uses [Kimi K3 Post-Training and Agentic RL](kimi-k3-posttraining-agentic-rl.md) — RL rollout pool, throttling, and AgentENV sandboxes that enable its agentic training.
- Related to [SGLang DSpark Speculative Decoding](sglang-dspark-speculative-decoding.md) — production speculative path consistent with KDA replay and prefix-cache preservation.
- Related to [Kimi K3 Local Deployment](kimi-k3.md) — same model served by these production techniques.

## Coverage limits

- Kernel, planner, and scheduler descriptions are architectural summaries; CUTLASS/Triton tuning parameters, ILP formulations, and exact autotuning coefficients were not compiled.
- Figures for KDA lower-bound compute, KCP layout, pipeline overlap, and prefix-cache hit were read from text/TikZ description; performance curves were not re-measured.
- Open-source links (MoonEP, AgentENV, FLA PR) were recorded as cited, not cloned or tested.

[^k3-infra]: Kimi K3 Technical Report — `../raw/arXiv-2607.24653v1/5-infrastructure.tex`, FlashKDA plus intra-device CP plus KCP all-gather composition, PP/VP plus EP plus ZeRO-1 plus Pipeline ZeRO-2 plus CP with overlapped all-to-all, MoonEP E/R bound plus planning plus zero-copy plus static shapes plus workload-aware GEMM, unified activation/MoE/AttnRes/PP-balance/grad-shard/P2P-Muon memory stack, dynamic-CP plus bubble-hidden ViT, external write-back KV pool plus auto-throttling plus grad-buffer reuse for RL, AgentENV Firecracker plus pause/fork/snapshot plus OverlayBD density plus 51M-sandbox totals, unified paged hybrid cache plus 512/6144 decoupled hashing plus two-stage lookup plus concurrency guards, KDA replay plus AttnRes SP/overlap/fusion plus LatentMoE fused/multimem/WarpDecode kernels, affinity plus budget fleet scheduling.
