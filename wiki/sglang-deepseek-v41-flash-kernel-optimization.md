---
type: Concept
title: SGLang DeepSeek-V4.1-Flash Kernel Optimization
description: BS=1 kernel journey on 4×GB300 taking DeepSeek-V4.1-Flash from 35.2 to 873.6 tokens/s via MXFP8 GEMM dispatch, small-operator and mHC fusion, DSpark verify kernels, and MoE TP4 with padding.
tags: [sglang, deepseek-v4.1, kernels, dspark, speculative-decoding, mhc, moe, mxfp8, benchmark]
status: stable
created: 2026-10-04
generated: { by: llm-wiki-agent/1, at: 2026-10-04T10:16:30Z }
stale_after: 2027-04-04
sources:
  - id: dsv41-kernel
    resource: ../raw/deepseek-v4-1-flash-kernel-optimization/index.md
    kind: article
    title: 'DeepSeek-V4.1 Flash on SGLang: from 35 to 873 tokens/s'
---

The SGLang team took single-request (BS=1) DeepSeek-V4.1-Flash decode on 4× GB300 with attention TP4 from 35.2 tokens/s on the first working build to 203.3 tokens/s with plain-decode kernel work. With DSpark at block size 5 and simulated acceptance, it then went from 558.24 to 873.63 tokens/s by fusing verify, MoE, indexer and compression kernels and moving MoE from EP4 to TP4 with padding[^dsv41-kernel]. All throughput numbers are **Reported** by the SGLang team, and none of them use the new kernels DeepSeek released with V4.1[^dsv41-kernel]. The 35→873 headline is not a like-for-like comparison: the workload changes between rounds 10 and 11, and DSpark acceptance is simulated (**Synthesis**, see [Interpretation](#interpretation)).

## Serving-relevant architecture

The source summarizes the V4.1-Flash changes that drive serving cost, citing the model config and technical report (**Reported**)[^dsv41-kernel]:

|  | V4 Flash | V4.1 Flash |
| --- | --- | --- |
| Backbone | 284B | 552B, plus 196B of Engram memory parameters |
| Active per token | ~13B | ~8B on input, ~16B on output |
| Structure | 43 decoder layers | 20 causal encoder layers + 20 decoder layers |
| Global attention | CSA / HCA | CSA2, KV and indices shared across layers |
| Global KV per token | 3,514 bytes | 890 bytes |

- **Prefill vs. decode.** The 20 decoder layers take their global KV from the encoder's final output, so most of a long prompt only runs through the first 20 layers. The decoder rebuilds its local window by replaying the last 128 tokens, which roughly halves backbone prefill work. Each generated token still runs all 40 layers, so decode does not get the same saving[^dsv41-kernel].
- **890-byte derivation.** Only layers 2, 8, 14 and 20 produce global KV. The first three pool two tokens per entry and layer 20 keeps one entry per token. Each FP4 entry holds a 288-byte main KV and a 68-byte indexer K, giving `(288 + 68) × (3/2 + 1) = 890` bytes per original token[^dsv41-kernel]. The arithmetic checks out (**Reproduced** by recomputation). DeepSeek puts the SSD cache requirement at about an eighth of before, because the local window can always be rebuilt by replay[^dsv41-kernel].
- **Logical vs. allocated size.** 890 bytes is the logical size. Some SGLang paths still use a FlashMLA-compatible cache layout, so the memory actually allocated is different[^dsv41-kernel].
- **Where the kernel work comes from.** CSA2's hierarchical candidate filter means only the top-512 global positions reach attention, and Engram adds conditional memory through n-gram lookups. Both brought their own indexing, normalization and fusion work[^dsv41-kernel]. Model details are in [DeepSeek-V4.1-Flash Architecture](deepseek-v41-architecture.md).

## Optimization rounds

Round labels and values come from the opening journey chart's per-point titles. Rounds 1–10 are plain decode using the original measurements. Rounds 11–16 use DSpark on random 4k/1k with a simulated accept length of 5.5[^dsv41-kernel].

| Round | Change | BS=1 tokens/s |
| --- | --- | --- |
| 1 | First working build | 35.2 |
| 2 | MXFP8 GEMM | 117.8 |
| 3 | RoPE + FP4 fusion | 133.5 |
| 4 | mHC row tiles by input rows | 141.1 |
| 5 | Reduce + Sinkhorn fusion | 146.5 |
| 6 | Cross-layer shared scratch | 148.4 |
| 7 | C2 pooling fusion | 152.1 |
| 8 | mHC statistics overlap | 186.4 |
| 9 | Fast paths on by default | 186.6 |
| 10 | GEMV / norm / Engram gate | 203.3 |
| 11 | DSpark on | 558.2 |
| 12 | Verify / MoE fusion | 718.8 |
| 13 | Small-batch projections / mHC | 761.7 |
| 14 | Indexer post-processing / projection fusion | 802.4 |
| 15 | C2 verify compression fusion | 853.5 |
| 16 | MoE TP4 + padding | 873.6 |

## Plain-decode techniques (rounds 1–10)

- **Check GEMM dispatch first.** Some dense weights ship in FP8, but their quantization block and scale layout did not match what the backend expected, so those GEMMs fell back to a slower path. SGLang now rearranges the scale layout once at weight load, and those GEMMs go straight into the Blackwell MXFP8 GEMM: 35.2 → 117.8 tokens/s. The source's lesson is that, when bringing up a new model, checking which kernel a GEMM actually dispatches to is usually worth more than tuning tiles[^dsv41-kernel].
- **Neighbor fusion in the decode chain.** In decode, RoPE, FP4 quantization, compressor pooling, RMSNorm and the cache write feed straight into each other, so fusing neighbors saves a launch and a trip through memory each time. RoPE + FP4 fuses rotation, quantization and dequantization (117.8 → 133.5). The C2 compressor fuses normalization, pooling and the state write for adjacent tokens (148.4 → 152.1). Single-row projections such as WO-A use GEMV, and the small norms and the Engram gate get fused kernels (186.6 → 203.3)[^dsv41-kernel].
- **Shared per-step state.** Per-step request indices and scratch buffers are now built once and shared across layers instead of being rebuilt in every layer (146.5 → 148.4). Once validated, the fast paths were turned on by default[^dsv41-kernel].
- **mHC reduction.** mHC keeps four residual streams. For every attention and MoE sublayer it computes mixing coefficients and normalizes them with Sinkhorn. Each step is cheap, but at small batch the per-sublayer cost adds up. Picking tile sizes from the number of input rows (133.5 → 141.1) and then fusing the statistics reduction with Sinkhorn (→ 146.5) addressed this[^dsv41-kernel].
- **Single-pass mHC overlap.** Pre-mix uses the previous sublayer's coefficients, so this sublayer's statistics and Sinkhorn can run on a separate stream in parallel with attention or MoE, joining before post-mix. Together with compressor and indexer fusion and overlap, this took BS=1 from about 152 to 186 tokens/s, the largest plain-decode gain after MXFP8[^dsv41-kernel].

## DSpark verify adaptation (rounds 11–16)

DSpark ships in the official checkpoint as three lightweight draft blocks. They read hidden states from the main model's last few layers, produce logits for several positions at once, resolve dependencies between draft tokens with a Markov head, and hand the block to the target for batched verification[^dsv41-kernel]. With block size 5 plus the anchor, target verify handles up to 6 rows for a single request. That broke the plain-decode assumption of one row per request, so the M=1 fast paths had to be reworked[^dsv41-kernel].

The launch sets `SGLANG_RAGGED_VERIFY_MODE=static`[^dsv41-kernel], which is the full-block verify baseline in [SGLang DSpark Speculative Decoding](sglang-dspark-speculative-decoding.md). These results therefore measure kernel cost without confidence-trimmed `compact` scheduling (**Synthesis**).

- **Verify and MoE fusion (558.24 → 718.75).** The mHC overlap now also runs in verify and draft. WO-A writes directly into the layout the next stage needs. The candidate mask fuses the valid-length check with candidate handling, which cuts scans over large buffers. On the MoE side, the router emits the layout the experts need, input quantization overlaps routing, and the expert-weighted reduction, shared-expert add and all-reduce run as one step, which cuts intermediate write-back[^dsv41-kernel].
- **Small-batch projections and normalization (→ 761.71).** WO-A uses split-K so more thread blocks work at once. mHC fuses the mixing of the four residual streams with RMSNorm. The draft's KV projections reuse the MXFP8 weights and scales instead of the old FP8 path[^dsv41-kernel].
- **Indexer post-processing and projections (→ 802.38).** The post-Top-K score check, invalid-position filtering and KV page address translation are now one step, and chosen candidate blocks expand straight into a token mask. Q's RoPE is merged into the attention buffer write, and WO-A's split-K reduction does the following MXFP8 quantization itself, skipping an intermediate tensor[^dsv41-kernel].
- **C2 verify compression (→ 853.49, accept 5.520).** In L2, L8 and L14 (numbered from 0), verify used to run a chain of small operators to find the previous token, handle the mask, pool, and write the cache. Verify positions are contiguous, so within a request the previous row can be read directly and only the first row needs the ring buffer. Pair pooling, RMSNorm, RoPE, quantization and the main KV write are fused into one kernel, and the same fused write is reused for index-K[^dsv41-kernel].
- **MoE TP4 with padding (→ 873.63).** Under TP4 the expert intermediate dimension is 576 per GPU, padded to 640 at load time to fit the kernel. Every GPU computes a different slice of the same experts, so uneven expert load causes less waiting between ranks. In a same-round comparison with every earlier optimization in place, EP4 gave 854.64 and TP4 873.63 tokens/s (+2.22%). The median gap between ranks arriving at finalize fell from 11.14 to 3.40 µs[^dsv41-kernel]. 576 matches the 2,304 expert intermediate size in [DeepSeek-V4.1-Flash Architecture](deepseek-v41-architecture.md) divided by 4, and the padding adds about 11% expert compute per GPU (**Synthesis**).

| Configuration | BS=1 tokens/s | Measured accept length |
| --- | --- | --- |
| DSpark, before optimization | 558.24 | 5.505 |
| + verify / MoE fusion and overlap | 718.75 | 5.505 |
| + small-batch projections / mHC fusion | 761.71 | 5.505 |
| + indexer post-processing / Q RoPE / WO-A quantization | 802.38 | 5.505 |
| + C2 verify compression fusion | 853.49 | 5.520 |
| All optimizations, MoE TP4 + padding | 873.63 | 5.505 |

Over these rounds, DSpark output speed rose about 56.5%[^dsv41-kernel]. The 853.49 row is the measurement taken when C2 verify fusion landed. The 2.22% figure comes from the separate EP4/TP4 comparison round, which is why 854.64 and 853.49 differ[^dsv41-kernel].

## Benchmark protocol and reproduction

**Stack.** [BBuf/sglang@835c3909](https://github.com/BBuf/sglang/tree/835c39094ad017c2f54f8ea598002e669e6fa30d), checkpoint `deepseek-ai/DeepSeek-V4.1-Flash` at revision `dba1be0a`, 4× GB300, PyTorch 2.13.0+cu130, FlashInfer 0.6.18, Triton 3.7.1, sglang-kernel 0.4.6.post1, sgl-deep-gemm 0.1.7, and CUTLASS DSL 4.6.2[^dsv41-kernel].

**TP4 launch behind 873.63 tokens/s**, run from the checkout root. `--tp 4 --ep-size 1` puts both attention and MoE on TP4, and this version applies the padding at weight load. For the EP4 comparison, change only `--ep-size 4`[^dsv41-kernel]:

```bash
export MODEL_PATH=/path/to/DeepSeek-V4.1-Flash
export SGLANG_RAGGED_VERIFY_MODE=static
export SGLANG_SIMULATE_ACC_LEN=5.5
export SGLANG_SIMULATE_ACC_METHOD=match-expected
CUDA_VISIBLE_DEVICES=0,1,2,3 PYTHONPATH="$PWD/python" MAX_JOBS=16 \
python -m sglang.launch_server \
  --model-path "$MODEL_PATH" \
  --served-model-name deepseek-ai/DeepSeek-V4.1-Flash \
  --tp 4 --ep-size 1 --trust-remote-code \
  --moe-a2a-backend none --moe-runner-backend flashinfer_mxfp4 \
  --mem-fraction-static 0.80 --max-total-tokens 33554432 \
  --chunked-prefill-size 4096 \
  --cuda-graph-bs-decode 1 2 4 8 16 32 64 \
  --max-running-requests 128 \
  --speculative-algorithm DSPARK --speculative-dspark-block-size 5 \
  --skip-server-warmup --reasoning-parser deepseek-v41 \
  --random-seed 42 --decode-log-interval 10 \
  --host 127.0.0.1 --port 30021
```

**Workload.** With random seed 42, special tokens are excluded from the vocabulary and 4,096 token ids are drawn uniformly. The ids are sent directly with no chat template, and every configuration reuses the same `prompt.json`. Output is fixed at 1,024 tokens[^dsv41-kernel].

**Harness.** `benchmark.py bench --max-tokens 1024 --repeat 6` posts to `/generate` with `temperature=0` and `ignore_eos=True`, and checks on every run that input is 4,096 tokens and output is 1,024. It calls `/freeze_gc` after startup, clears the cache before each run, and discards one warm-up. Each launch is measured for 6 runs. The configurations from round 13 on were each launched twice, with the median taken over 12 runs. The EP4/TP4 round alternated TP, EP, TP, EP, kept every measurement, and had the profiler off[^dsv41-kernel].

**Metric.** Throughput is the tokens added after the first streamed event divided by the time from the first event to the last, so it excludes full prefill and is not TTFT-inclusive. Accept length counts the token the target produces, so the ceiling at block size 5 is 6[^dsv41-kernel].

**Simulated acceptance.** `match-expected` accepts 5 or 6 tokens each round, so the expected accept length is 5.5. A finite number of rounds and truncation at the last step move the measured value slightly. Because acceptance is simulated, generated text is not used to judge quality, and simulation mode also disables the in-graph acceptance path[^dsv41-kernel].

| Same code, same input, attention TP4 | DSpark off · EP4 | DSpark on · EP4 | DSpark on · TP4 + padding |
| --- | --- | --- | --- |
| BS=1 output tokens/s | 223.50 | 853.49 | 873.63 |
| Measured accept length (target 5.5) | — | 5.520 | 5.505 |

Under these conditions, DSpark at simulated acceptance 5.5 gives about 3.82× (EP4) and 3.91× (TP4 + padding) over DSpark-off EP4 (**Synthesis**, computed from the reported table)[^dsv41-kernel].

## Interpretation

These points are **Synthesis** drawn from the cited measurements:

- **Like-for-like speedups.** The chart's 35.2 → 873.6 (~24.8×) spans a workload change between rounds 10 and 11, which the chart draws as a dashed segment, plus DSpark with simulated acceptance. The comparable pairs are 35.2 → 203.3 for plain-decode kernels on the original workload, 558.24 → 873.63 for DSpark-path kernels, and 223.50 → 873.63 for DSpark on vs. off with the final code.
- **Don't mix the two plain-decode numbers.** 203.3 (round 10, original workload) and 223.50 (DSpark off, random 4k/1k, final code) differ in both workload and code, so they should not be compared directly.
- **Real acceptance will differ.** Real DSpark throughput depends on real acceptance, which varies by workload. 5.5 is near the block-5 ceiling of 6, and simulation bypasses the in-graph acceptance path, so production BS=1 numbers can be lower.
- **Where BS=1 time goes.** At BS=1 the wins come mostly from removing launches, intermediate writes and cross-rank waiting, not from raising FLOP throughput. The order of attack was fixing kernel dispatch, fusing small-operator chains, overlapping independent streams, specializing for the few-row verify shapes, then rebalancing MoE parallelism.
- **TP vs. EP for MoE at tiny batch.** EP4 concentrates each expert on one rank, so with few tokens per step, uneven routing leaves ranks idle at finalize. TP4 spreads every expert across all ranks at the cost of padding overhead. The measured gain here was modest (2.22%) and specific to this BS=1 configuration. See [SGLang Expert Parallelism](sglang-expert-parallelism.md) for the general EP backends.

## Relationships

- Uses [DeepSeek-V4.1-Flash Architecture](deepseek-v41-architecture.md): the CED, CSA2, Single-Pass mHC, Engram, DSpark and FP4 KV designs these kernels target.
- Related to [SGLang DeepSeek-V4.1 Inference](sglang-deepseek-v41-inference.md): the day-0 serving stack whose mHC overlap, Sinkhorn fusion, ratio-2 pooling and single-token GEMV work this page measures round by round.
- Related to [DeepSeek-V4.1-Flash Systems](deepseek-v41-systems.md): DeepSeek's own fused-kernel deployment (Mega-mHC, Mega-MoE and similar), which these SGLang results explicitly do not use, plus the 890-byte KV and 1/8 SSD figures restated here.
- Uses [SGLang DSpark Speculative Decoding](sglang-dspark-speculative-decoding.md): the DSPARK algorithm, the `static` ragged verify mode and the `SGLANG_SIMULATE_ACC_LEN` simulation used in rounds 11–16.
- Related to [SGLang Expert Parallelism](sglang-expert-parallelism.md): `--moe-a2a-backend none` with `--moe-runner-backend flashinfer_mxfp4`, and the EP4-vs-TP4 MoE choice at BS=1.
- Related to [SGLang DeepSeek-V4 Inference](sglang-deepseek-v4-inference.md): the predecessor's TileLang split-K mHC and MXFP8×MXFP4 MoE paths, against which the V4.1 small-batch mHC and WO-A split-K work can be compared.
- Related to [SGLang GLM-5.2 NVFP4 Optimization](sglang-glm52-optimization.md): a comparable SGLang single-user kernel-optimization journey on Blackwell with speculative decoding and indexer fusion.
- Uses [SGLang Server Arguments](sglang-server-arguments.md): the general launch-flag reference. `--cuda-graph-bs-decode` and `--speculative-dspark-block-size` are used as shown on the pinned fork.

## Coverage limits

- The only local artifact is the entry-point capture. Its four inline SVGs (journey chart, encoder-decoder/KV diagram, mHC overlap diagram and DSpark verify diagram) were inspected as text. Round values come from SVG `<title>` elements, which match the prose wherever the prose gives a number[^dsv41-kernel].
- Linked artifacts were not available locally and were not inspected: `launch-tp4.sh`, `prompt.json`, `benchmark.py`, the per-run results, the kernel sources at the pinned commit (`dsv4/c2.py`, `indexer_postprocess.py`, `q_rope_store.py`, `wo_a_bf16_small_batch.py`), the SGLang cookbook, the `dsv4.1` branch and the Miles docs. The day-0 post and the technical report it links are already compiled in [SGLang DeepSeek-V4.1 Inference](sglang-deepseek-v41-inference.md) and [DeepSeek-V4.1-Flash Architecture](deepseek-v41-architecture.md)[^dsv41-kernel].
- The workload for plain-decode rounds 1–10 ("original measurements") is not specified beyond BS=1 on the same hardware, so those values are **Reported** without full workload shape. The source gives no publication date, and the capture postdates the 2026-09-10 day-0 post it links[^dsv41-kernel].
- Flags and environment variables were used on the `BBuf/sglang` fork at `835c3909`, not a mainline release, and may change. Commands were not executed. The acknowledgments mention that some kernels were developed with the KDA 0.5 framework, but no detail is given[^dsv41-kernel].

[^dsv41-kernel]: DeepSeek-V4.1 Flash on SGLang: from 35 to 873 tokens/s (SGLang Team, sglang.io) — `../raw/deepseek-v4-1-flash-kernel-optimization/index.md`. Locators: opening journey SVG per-round `<title>` values; "Architecture changes and KV cache compression" (V4/V4.1 table, KV formula, logical-size caveat); "Kernel optimizations for plain decode" → "FP8 GEMM: 35 → 118 tokens/s", "Small-operator fusion and GEMV" (fusion table), "mHC: reduction fusion and overlap"; "DSpark adaptation and optimization" (verify/MoE, small-batch, indexer, C2 verify, MoE TP4 paragraphs and configuration table, closing note on DeepSeek kernels); "How to reproduce: random 4k/1k, simulated accept length fixed at 5.5" (stack versions, TP4 command, input, harness, `match-expected`, metric definition, DSpark off/on table); "Acknowledgments" (KDA 0.5).
