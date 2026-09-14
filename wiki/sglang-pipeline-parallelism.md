---
type: Concept
title: SGLang Pipeline Parallelism
description: Pipeline-parallel long-context serving in SGLang with async micro-batching, dynamic chunked prefill, and PP-size tuning.
tags: [sglang, pipeline-parallelism, long-context, chunked-prefill]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:31:27Z }
sources:
  - id: sgl-pp
    resource: ../raw/sglang/advanced_features/pipeline_parallelism.mdx
    title: Pipeline Parallelism for Long Context
  - id: sgl-pp-chunked
    resource: ../raw/2026-01-15-chunked-pipeline/index.md
    title: 'Pipeline Parallelism in SGLang: Scaling to Million-Token Contexts and Beyond'
  - id: qwen38-day0
    resource: ../raw/2026-08-12-qwen3-8-day0-support/index.md
    title: 'SGLang and Miles Add Day-0 Support for Qwen3.8'
---

SGLang uses pipeline parallelism (PP) with chunked pipeline parallelism, async P2P micro-batching, and dynamic chunked prefill to reduce time-to-first-token (TTFT) for ultra-long inputs and to scale across nodes with less communication than tensor parallelism[^sgl-pp][^sgl-pp-chunked].

## Why pipeline parallelism

KV-cache techniques remove redundant computation but do not remove the large initial-input (ITL) TTFT cost of ultra-long sequences[^sgl-pp][^sgl-pp-chunked]:

- Tensor parallelism (TP) is the conventional intra-node approach but hits All-Reduce communication bottlenecks in multi-node deployments.
- Context parallelism (CP) needs per-layer All-Gather of KV states and intrusive attention changes.
- Pipeline parallelism only communicates hidden states at pipeline-stage boundaries with point-to-point send/recv, so volume stays nearly constant as layers-per-stage grow.

The chunked-pipeline analysis formalizes this with `B` batch size, `S` sequence length, `H` hidden size, `H_KV` KV hidden size, `L` layers, `M` micro-batches, and `P` stages[^sgl-pp-chunked]:

```text
Commu(TP) ~= 4 * B * S * H * L * bytes (2x All-Reduce per layer)
Commu(CP) ~= 2 * B * S * H_KV * L * bytes (All-Gather per layer)
Commu(PP) = B * S * H * (P - 1) * bytes (P2P only at stage boundaries)
```

In multi-node deployments where `P << L`, PP gives a nearly order-of-magnitude smaller volume than TP[^sgl-pp-chunked].

Bubble trade-off[^sgl-pp-chunked]:

```text
Bubble Ratio = (P - 1) / (P - 1 + M)
```

TP and CP are theoretically bubble-free, while PP pays bubbles that become negligible when `M >> P` for long-context prefill. For fixed workload `M`, raising `P` raises bubbles, so the recommended shape is bubble-free TP/CP intra-node over NVLink plus PP cross-node[^sgl-pp-chunked].

| Metric | TP | CP | PP |
| --- | --- | --- | --- |
| Split dimension | Hidden `H` | Sequence `S` | Layers `L` |
| Communication | AllReduce per layer | AllGather per layer | P2P send/recv |
| Volume | High | Medium | Low |
| Bubble ratio | 0 | 0 | `(P-1)/(P-1+M)` |
| Implementation | Low | High, attention-specific | Medium |
| Generality | High | Low | High |

TP generality is further limited because MoE FFN quantization blocks sometimes cannot align with large-TP partitions, precluding large TP even before bandwidth is considered[^sgl-pp-chunked].

## The bubble and the memory wall

Traditional PP partitions layers across Stage 1..N and works for short prompts, but prompts beyond 128K or 1M tokens expose[^sgl-pp-chunked]:

1. **Pipeline bubble:** monolithic batches leave downstream GPUs idle while waiting for the first stage.
2. **Memory wall:** one pass over a 1M-token prompt must hold and communicate intermediate hidden states for the whole sequence, spiking peak memory.

## Chunked pipeline parallelism

Instead of one forward pass, SGLang partitions the prompt into chunks such as 4K or 6K tokens that flow like micro-batches: as soon as Stage 1 finishes Chunk 1 and starts PP communication, it starts Chunk 2 while Stage 2 starts Chunk 1. Startup latency drops from total sequence length to first-chunk size[^sgl-pp-chunked].

This follows Mooncake, BladeLLM, and TeraPipe token-level pipelining ideas. SGLang pioneered support over six months before the blog via `#5724` and `#8846`[^sgl-pp-chunked].

With dynamic chunked prefill, each request's input tokens are partitioned into chunks no longer than the chunked-prefill size, and different chunks of the same request can be processed simultaneously on different nodes[^sgl-pp].

## Async micro-batching implementation

Chunked prefill plus PP still stalls when the GPU blocks on CPU metadata or network transfers. SGLang adds a micro-batching event loop with non-blocking async P2P to overlap GPU compute with CPU work and PP communication; implementation lives in `python/sglang/srt/managers/scheduler_pp_mixin.py`[^sgl-pp][^sgl-pp-chunked].

The early PP support since `#5724` and PD compatibility in `#8846` left headroom; the refactor adds the event loop first proposed in `#7979` and redesigned in `#11852`[^sgl-pp].

Key mechanisms[^sgl-pp][^sgl-pp-chunked]:

- **Decoupled sync/async event loop:** the scheduler uses `async_send` in `_pp_send_pyobj_to_next_stage`, returning a `P2PWork` handle instead of blocking; synchronization with `P2PWork.work.wait()` is deferred until `_pp_commit_comm_work`, so the CPU can schedule the next batch or process metadata while data is in flight.
- **Multi-stream execution:** besides the synchronizing `default_stream`, SGLang uses `forward_stream` for forward-pass compute and `copy_stream` for device-to-host transfers; while `_pp_launch_batch` runs the current micro-batch on GPU, the CPU processes the previous micro-batch result with `_pp_process_batch_result`.

## Dynamic chunking

Fixed-size chunked prefill causes above-theory bubbles at large PP because execution is non-uniform: identical chunk sizes take longer as prefix length `L` grows due to incremental self-attention, and the skew propagates to higher ranks[^sgl-pp][^sgl-pp-chunked].

SGLang predicts the next chunk size so that[^sgl-pp][^sgl-pp-chunked]:

```text
Runtime(L + Next Chunk Size) - Runtime(L) = Runtime(Initial Chunk Size)
```

It profiles requests with different ITLs, fits cumulative runtime as a quadratic function of sequence length, solves for the next chunk size at prefix length `L`, and progressively shrinks later chunks as `L` grows to keep stage times aligned[^sgl-pp][^sgl-pp-chunked]. The scheduler aligns the predicted value downward to the nearest multiple of `max(--page-size, 64)` for KV-cache management and hardware efficiency[^sgl-pp][^sgl-pp-chunked].

Configuration[^sgl-pp][^sgl-pp-chunked]:

- `--enable-dynamic-chunking` enables the mode; `--chunked-prefill-size` sets the initial chunk size and should be set larger than the fixed-mode optimum so there are not too many chunks.
- `SGLANG_DYNAMIC_CHUNKING_SMOOTH_FACTOR` controls adjustment aggressiveness, default `0.75`. `1` follows the quadratic model strictly; larger values change chunk size more aggressively with better potential performance but smaller tail chunks, possible degradation, and more total chunks; smaller values are more conservative with fewer chunks; `0` disables dynamic adjustment and equals fixed-size chunking.

## Tuning guidance

Because hardware, models, and workloads differ, dynamic chunking needs tuning[^sgl-pp][^sgl-pp-chunked]:

1. **Find the fixed-mode baseline:** iterate `--chunked-prefill-size` for the targeted PP size and ITL.
2. **Pick the dynamic initial size:** use 2–3x the optimal fixed size to reduce total chunks and avoid underutilizing “tail chunks”; the predictor keeps later chunks at least 1/4 of the initial size. For extremely large ITL, consider 4x the fixed optimum.
3. **Adjust the smooth factor:** `1.0` follows the model strictly; `0.6–0.85` is the recommended balance between dynamic scaling and hardware stability; `0` reverts to fixed chunking.

Layer-partition tip: when layers do not divide evenly, put the larger partition on the higher PP rank to keep it utilized while waiting for earlier stages, e.g. for DeepSeek-V3.1 `SGLANG_PP_LAYER_PARTITION=15,15,15,16` usually beats `16,15,15,15`[^sgl-pp][^sgl-pp-chunked].

## Long-context best practice

- Start tuning with a small chunked-prefill size such as 4K and increase until optimal for the model, hardware, PP size, and ITL, or size it from hardware capacity with a roofline model[^sgl-pp].
- Enable dynamic chunking plus smoothing-factor tuning for ultra-long ITL; this is experimental, needs tuning effort, and may not suit all workloads[^sgl-pp].

### H20 case study at 128K ITL

With fixed chunk sizes from 2K to 16K on NVIDIA H20, 4K gave the best prefill TTFT for DeepSeek-V3.1 and 6K for Qwen3-235B-A22B-FP8[^sgl-pp]. Scaling the fixed optimum by 3x as the dynamic initial size and tuning the default `0.75` smooth factor gave `0.65` with 12K initial chunks for DeepSeek-V3.1 and `0.8` with 18K initial chunks for Qwen3-235B-A22B-FP8[^sgl-pp][^sgl-pp-chunked].

Example shapes, all with `--disable-radix-cache --mem-fraction-static 0.8 --attention-backend fa3 --max-running-requests 128` on 4 nodes[^sgl-pp]:

- DeepSeek-V3.1 fixed: `--tp 8 --pp-size 4 --chunked-prefill-size 4096`.
- DeepSeek-V3.1 dynamic: `SGLANG_DYNAMIC_CHUNKING_SMOOTH_FACTOR=0.65`, `--tp 8 --pp-size 4 --chunked-prefill-size 12288 --enable-dynamic-chunking`.
- Qwen3-235B-A22B-FP8 fixed: `--tp 4 --pp-size 8 --chunked-prefill-size 6144`.
- Qwen3-235B-A22B-FP8 dynamic: `SGLANG_DYNAMIC_CHUNKING_SMOOTH_FACTOR=0.8`, `--tp 4 --pp-size 8 --chunked-prefill-size 18432 --enable-dynamic-chunking`.

`--disable-radix-cache` was for reproducible benchmarking only and is not recommended in production[^sgl-pp].

## Production compatibility: PD disaggregation and HiCache

PP prefill nodes can use high PP for long prompts while decode nodes use high TP for generation speed[^sgl-pp-chunked]:

- **Chunk-by-chunk KV transfer:** with Mooncake transfer backends, one chunk's KV moves from prefill to decode as soon as it completes instead of waiting for all chunks, cutting transfer overhead.
- **Hybrid shapes:** PP8 TP8 for heavy prefill combined with PP1 TP8, PP8 TP1, or PP1 DP16 EP16 for high-throughput decode, tuned to TTFT/TPOT targets.
- **Memory efficiency:** sharded weights lower per-GPU footprint, leaving room for larger KV cache and higher concurrency or max context.

For contexts beyond 128K, chunked PP composes with HiCache: radix-tree prefix matching at chunk granularity lets the PP pipeline skip chunks already in host or disk storage, cutting multi-turn and agentic TTFT for repeated long prefixes[^sgl-pp-chunked].

## Performance impact

Testbed is 6 H20 nodes with 8x96GB GPUs; DeepSeek-V3.1 PP1 128K baseline used a standalone 8x141GB H20 node because 96GB OOMs. Throughput is the mean over 16 consecutive requests. `DCK` means dynamic chunking initial size, `sigma` is the smooth factor. Contexts were overwritten to 1M only for analysis. TP32 for DeepSeek-V3.1 required skipping parts of weight loading plus `config.json` edits because MoE quantization blocks are indivisible by large TP; it is a hacked comparison baseline only[^sgl-pp-chunked].

- **PP vs TP:** PP2 TP8 beats PP1 TP16 on the same GPU count, and PP4 TP8 beats PP1 TP32 across chunk settings. The worst PP4 TP8 fixed-12288 case still beats the best pure-TP PP1 TP32 fixed-12288 case by 18.4%; with dynamic chunking the margin grows to 30.5%. Headline: PP4 TP8 gives 3.31x prefill throughput for DeepSeek-V3.1 over TP8 at 12K chunks, versus 2.54x for TP32[^sgl-pp-chunked].
- **Throughput scaling:** Qwen3-235B-A22B-FP8 DCK 18K reaches 6.14x on PP8 (32 GPUs) versus PP1 (4 GPUs). DeepSeek DCK 12K reaches 3.31x on PP4, marginally above static 4K at 3.20x[^sgl-pp-chunked].
- **Strong scaling efficiency at 128K ITL:** Qwen DCK 18K holds 76.9% at PP8 versus 69.6% for static 6K; DeepSeek holds 82.8% up to PP4. DCK is more resilient to bubble-driven decay[^sgl-pp-chunked].
- **TTFT reduction:** Qwen baseline about 55.5s on PP1 TP4 falls to about 10.5s on PP8 TP4, about 81.1% lower. DeepSeek baseline about 48.5s on PP1 TP8 falls to about 15.5s on PP4 TP8, about 67.9% lower; dynamic chunking beats fixed at each PP size[^sgl-pp-chunked].

TTFT versus ITL for Qwen3-235B-A22B-FP8 on PP8 TP4 H20[^sgl-pp-chunked]:

| ITL | 128K | 256K | 512K | 1M |
| --- | --- | --- | --- | --- |
| TTFT (s) | 10.54 | 32.68 | 114.33 | 420.91 |

Higher-compute or higher-bandwidth hardware than H20, or larger PP across more nodes such as PP8 TP16 for DeepSeek-V3.1, should further cut million-token TTFT[^sgl-pp-chunked].

## Getting started

Requires SGLang `>= v0.5.7`. Set `--pp-size` and `--chunked-prefill-size`; add `--enable-dynamic-chunking` plus `SGLANG_DYNAMIC_CHUNKING_SMOOTH_FACTOR` for dynamic mode[^sgl-pp-chunked]:

```bash
# DeepSeek-V3.1 128K, 32 GPUs: fixed chunks
python3 -m sglang.launch_server \
  --model-path deepseek-ai/DeepSeek-V3.1 --trust-remote-code \
  --nnodes 4 --node-rank 0 --tp 8 --pp-size 4 \
  --port 30000 --dist-init-addr <MASTER_NODE_IP> \
  --mem-fraction-static 0.8 --attention-backend fa3 \
  --host 0.0.0.0 --watchdog-timeout 3600 \
  --max-running-requests 128 --chunked-prefill-size 4096

# DeepSeek-V3.1 128K, 32 GPUs: dynamic chunking
export SGLANG_DYNAMIC_CHUNKING_SMOOTH_FACTOR=0.65
python3 -m sglang.launch_server \
  --model-path deepseek-ai/DeepSeek-V3.1 --trust-remote-code \
  --nnodes 4 --node-rank 0 --tp 8 --pp-size 4 \
  --port 30000 --dist-init-addr <MASTER_NODE_IP> \
  --mem-fraction-static 0.8 --attention-backend fa3 \
  --host 0.0.0.0 --watchdog-timeout 3600 \
  --max-running-requests 128 --chunked-prefill-size 12288 --enable-dynamic-chunking
```

Qwen shapes replace `--tp 4 --pp-size 8 --chunked-prefill-size 6144` fixed and `--chunked-prefill-size 18432 --enable-dynamic-chunking` with smooth factor `0.8` for dynamic mode[^sgl-pp-chunked].

## Qwen3.8 phase-split PP prefill

Qwen3.8 splits parallelism by phase under PD disaggregation: pure PP prefill with full-width GEMMs and no MoE dispatch/combine/EPLB beats wide-EP with EPLB at 8K prefill, while decode keeps wide-EP to shard all 512 experts[^qwen38-day0]: FP8 PP16 5231 versus 3421 input tok/s/GPU (1.53x) on 16 GPUs, and NVFP4 PP8 8363 versus 5151 (1.62x) on 8 GPUs[^qwen38-day0]. PP prefill is made composable with MTP by placing the draft head on the last stage with its own copy of the missing half and staging draft KV across the PD boundary, so prefill topology stays a free variable[^qwen38-day0]. Full parallel shapes and Pareto endpoints are maintained in [SGLang Qwen3.8 Inference](sglang-qwen3.8-inference.md).

## Future roadmap

2026 H1 PP work items are CP compatibility with PP `PP x CP` Part II, decode-side PP with performance tuning, and better runtime fitting plus chunking strategy for dynamic chunking; tracking is in the PP Roadmap issue `11857`[^sgl-pp-chunked].

## Relationships

- Uses [SGLang PD Disaggregation](sglang-pd-disaggregation.md) — PP implementation is compatible with PD disaggregation; high-PP prefill can pair with high-TP decode plus chunk-by-chunk Mooncake KV transfer.
- Uses [SGLang HiCache System Design](sglang-hicache-design.md) — chunk-granularity radix-tree prefix hits let the PP pipeline skip cached chunks for repeated ultra-long prefixes.
- Uses [SGLang Hyperparameter Tuning](sglang-hyperparameter-tuning.md) — shared `--chunked-prefill-size` / `--mem-fraction-static` / `--max-running-requests` sizing, with OOM versus prefill-speed trade-offs.
- Uses [vLLM Tensor and Pipeline Parallel Scaling](vllm-parallelism-scaling.md) — vLLM-side TP/PP strategy and multi-node runtime analog for comparing stage-boundary versus sharded-weight communication.
- Uses [vLLM Context Parallel Deployment](vllm-context-parallel-deployment.md) — CP sharding analog for the TP/CP/PP communication-versus-bubble choice.
- Related to [SGLang Qwen3.8 Inference](sglang-qwen3.8-inference.md) — Qwen3.8 phase-split pure-PP prefill versus wide-EP decode with last-stage draft-head MTP composition.

## Coverage limits

- Eleven local chart/diagram assets under `../raw/2026-01-15-chunked-pipeline/assets/` were enumerated; numeric claims above come from prose and Table 1, not pixel re-measurement. Pipeline-bubble diagrams and rank profiles are summarized as bubble reduction, not re-quantified[^sgl-pp-chunked].
- The LMSYS PP PRs `#5724` / `#8846` / `#7979` / `#11852`, roofline-model procedure, and PP Roadmap issue were referenced but not inspected; detail beyond the summary above is outside verified scope[^sgl-pp][^sgl-pp-chunked].
- TP32 DeepSeek numbers depend on a hacked weight-loading plus `config.json` workaround for quantization-block indivisibility; treat as directional PP-vs-TP evidence, not a supported deployment shape[^sgl-pp-chunked].
- No PP-with-PD-disaggregation launch procedure beyond flags and hybrid shapes, and no PP `PP x CP` procedure, were in these sources[^sgl-pp][^sgl-pp-chunked].

[^sgl-pp]: Pipeline Parallelism for Long Context — `../raw/sglang/advanced_features/pipeline_parallelism.mdx`, covering PP versus TP for ultra-long ITL/TTFT, async micro-batching event loop with `async_send` / `P2PWork` / `_pp_commit_comm_work` and `forward_stream` / `copy_stream` / `_pp_launch_batch` / `_pp_process_batch_result`, dynamic-chunking quadratic model with `max(--page-size, 64)` alignment, `--enable-dynamic-chunking` / `--chunked-prefill-size` / `SGLANG_DYNAMIC_CHUNKING_SMOOTH_FACTOR` semantics, 2–3x initial-size and 0.6–0.85 smoothing tuning steps, `SGLANG_PP_LAYER_PARTITION` placement tip, H20 128K DeepSeek-V3.1 and Qwen3-235B-A22B-FP8 launch shapes, and benchmarking-only `--disable-radix-cache` note.
[^sgl-pp-chunked]: Pipeline Parallelism in SGLang: Scaling to Million-Token Contexts and Beyond — `../raw/2026-01-15-chunked-pipeline/index.md`, covering TL;DR 3.31x DeepSeek PP4-TP8 throughput, 30.5% margin over TP32, 67.9% DeepSeek and 81.1% Qwen TTFT cuts, 82.8% DeepSeek and 76.9% Qwen DCK strong-scaling efficiency, TP/CP/PP volume formulas, `(P-1)/(P-1+M)` bubble ratio, comparison table, 128K/1M bubble and memory-wall framing, Mooncake/BladeLLM/TeraPipe-inspired CPP, async `scheduler_pp_mixin.py` event loop, `Runtime(L+ΔL)-Runtime(L)=Runtime(initial)` quadratic dynamic chunking with `max(--page-size,64)` alignment and default smooth factor 0.75, 3-step tuning plus `SGLANG_PP_LAYER_PARTITION=15,15,15,16` tip, Mooncake chunk-by-chunk PD transfer and hybrid PP/TP/DP/EP shapes, HiCache chunk-skip behavior, 6xH20 testbed with 16-request throughput means and 1M TTFT table (10.54s/32.68s/114.33s/420.91s), `>=v0.5.7` launch examples, and 2026-H1 CP/decode/fitting roadmap.
[^qwen38-day0]: SGLang and Miles Add Day-0 Support for Qwen3.8 — `../raw/2026-08-12-qwen3-8-day0-support/index.md`, covering phase-split pure-PP prefill versus wide-EP decode with 1.53x/1.62x 8K table and last-stage draft-head MTP composition.
