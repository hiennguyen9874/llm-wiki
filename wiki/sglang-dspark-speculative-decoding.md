---
type: Concept
title: SGLang DSpark Speculative Decoding
description: Confidence-driven variable-length verification with semi-autoregressive block drafting and ragged CUDA-graph verify for dense and sparse models.
tags: [sglang, speculative-decoding, dspark, cuda-graphs]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T15:00:00Z }
sources:
  - id: dspark-sglang
    resource: ../raw/2026-07-06-dspark-sglang/index.md
    title: "DSpark in SGLang: Speculative Decoding with Confidence-Driven, Variable-Length Verification"
  - id: kimi-k3-dspark
    resource: ../raw/Kimi-K3-DSpark.md
    title: Kimi K3 DSpark speculator
  - id: qwen38-dspark
    resource: ../raw/Qwen3.8-27B-DSpark.md
    title: Qwen3.8-27B-DSpark
---

DSpark trades fixed full-block verification for confidence-driven per-request verify budgets, pairing a semi-autoregressive block drafter with a scheduler that stops verifying tokens unlikely to be accepted; SGLang serves it with ragged per-request verify under full CUDA graphs, an overlap-aware speculative path, an additive step-cost table, and ceiling observability[^dspark-sglang].

## Why variable verify length

Speculative decoding trades extra compute for fewer decode steps, and the trade sours as load grows: at batch size `B` with `K` speculative tokens the target verifies `B * K` tokens every step, and past a point that costs more than it saves[^dspark-sglang]. DSpark attacks both ends — a block drafter that keeps acceptance high with one draft forward per block, and a variable verify length that trims the unlikely tail[^dspark-sglang].

SGLang supports DSpark on dense and sparse models such as Qwen3 and DeepSeek-V4; the integration is `sgl-project/sglang#30261` with roadmap `sgl-project/sglang#30344`[^dspark-sglang]. Reported gains reproduce the shape of the DSpark paper's mechanism and curve on an open engine, not its numbers to the digit, with every "faster" measured against identical non-spec or MTP controls[^dspark-sglang].

## Algorithm: block drafter, confidence head, STS

The adopted DSpark algorithm lives in three draft-side pieces[^dspark-sglang]:

- **Block drafter** — dense line for Qwen3 and sparse line for DeepSeek-V4; one forward emits a `gamma`-token block with a lightweight sequential head (Markov or RNN) conditioning each step on the previous token, so the block is semi-autoregressive.
- **Confidence head** — scores each drafted token's chance of surviving verification; the product across the block is the block's survival probability.
- **Sequential Temperature Scaling (STS)** — calibrates those scores so survival reflects the true acceptance rate the scheduler budgets against.

Around that, SGLang adds the serving surface: confidence scheduler, per-request ragged verify, full CUDA graph over ragged verify, acceptance-ceiling observability, additive SPS cost table, data-parallel attention support, zero-overhead scheduling integration, fused Triton kernels, and sharded block-drafter matmul[^dspark-sglang].

## Verify modes

The three modes are the axis the rest of the design turns on[^dspark-sglang]:

| Mode | Behavior |
| --- | --- |
| `static` | Verifies the full drafted block every step; the baseline. |
| `compact` | Verifies only the scheduler-picked per-request window; the production path. |
| `cap-accept` | Verifies the full block but commits only up to the window: same output as `compact` while exposing what full verify would have accepted. |

`compact` versus `no-trim` A/Bs run `static` full-block scheduling through the same ragged path to isolate the scheduling win from path effects[^dspark-sglang]. `SGLANG_RAGGED_VERIFY_MODE=compact|static` selects the path, with `SGLANG_DSPARK_ENABLE_SPS_RECORD` and `SGLANG_SIMULATE_ACC_LEN` used for cost-table profiling runs[^dspark-sglang].

## Ragged verify under full CUDA graphs

Per-request windows do not fit a fixed-shape CUDA graph: padding every request to the full block width pads the trim back in[^dspark-sglang]. SGLang keeps the batch ragged and keys the graph on the total token count — front-packing variable-length requests into one compact buffer and rounding only the total up to the nearest captured tier[^dspark-sglang]. Trimmed batches therefore replay a genuinely smaller graph with fewer attention and MLP rows, not a masked full-width forward; under DP attention the ranks share one tier (the largest any rank needs) and step down together[^dspark-sglang].

The packed buffer is a `cu_seqlens`-style varlen input reusing backend attention kernels — on DeepSeek-V4 the model's own sparse-MLA path (`flash_mla`) with no new kernel; each backend rebuilds its varlen metadata from the packed layout on graph replay[^dspark-sglang].

## Observability: ceiling under trimming

Trimming censors the ceiling: `compact` only verifies the window prefix, so the full-block acceptance count is never observed and a good trim cannot be told from a lossy one without extra data[^dspark-sglang]. A `cap-accept` companion run recovers it while committing exactly what `compact` commits, plus per-request confidence and calibration metrics such as ECE for post-hoc analysis[^dspark-sglang].

A block-accept estimator recovers the censored ceiling inside a production `compact` run without a companion, using future-step utilization of target tokens with logprobs to compute estimation intervals for the counterfactual tail, assuming property similarity of anchor tokens in trimmed versus untrimmed trajectories[^dspark-sglang].

## Scheduler behavior

The confidence scheduler converts per-block survival into a per-request verify budget each step via per-step SPS-argmax against the cost table; the reported version is vanilla proof that the mechanism works end to end, not a tuned result[^dspark-sglang].

Dynamic trim wins mainly at high batch: at batch 1 target verify cost is flat in tokens so trimming saves little and `compact` ties `no-trim`; as concurrency grows and throughput plateaus, shorter steps pull `compact` ahead[^dspark-sglang]. The gap is larger and opens earlier on lower-acceptance workloads because lower acceptance leaves more tail to trim, as the cost model predicts[^dspark-sglang]. The two reported examples are not a strict single-variable pair — they differ slightly in prompt formatting and per-arm round count — so read the trend, not absolute cross-panel numbers[^dspark-sglang].

Mixed traffic shows per-request differentiation: on gsm8k (high), arena-hard (mid), and poetry (low) the mean windows are 5.24, 3.78, and 2.91 tokens with 0.88–0.97 utilization against the untrimmed ceiling[^dspark-sglang]. About 55% of gsm8k steps fill the full window of six while about 80% of poetry steps use three or fewer, showing per-request sizing rather than one batch average[^dspark-sglang].

## Cost model

Step time `T(bs, K)` — `K` the batch's extra verify tokens — uses an additive fit `T(bs, K) = bias + alpha(bs) + theta(M)` with `M = bs + K`, where `alpha(bs)` is the request-scaling floor (draft pass plus part of attention) unmoved by trimming and `theta(M)` is the target verify-token cost, the only term trimming recovers[^dspark-sglang]. The scheduler's argmax trades expected accepted tokens against real marginal cost, so headroom appears only where `theta` is large; live-server checks validate predicted versus measured step time[^dspark-sglang]. The current SPS and calibration fit is a first approximation that may not fully capture context-length dependence, so the operating point is likely improvable[^dspark-sglang].

## Performance and engineering

DSpark gives the best throughput/latency trade-off across a 1–256 concurrency sweep on DeepSeek-V4-Flash, H200 DP-attention over four ranks, ahead of both the non-spec floor and the MTP EAGLE-style baseline (per-batch-size best of 1-1-2 and 3-1-4 configs)[^dspark-sglang].

Wall-clock work is twofold: cheaper steps and a hidden scheduler[^dspark-sglang]:

- Fused Triton kernels for compact scatter, SWA page-index, verify-length top-k scheduling, and ragged-window packing; folded block-drafter sampling path and sharded drafter matmul. One profile cites ~1.7 ms saved outside target verify against a 7.3 ms verify.
- Zero-overhead overlap scheduling: DSpark joins the spec-v2 runtime as a first-class worker with async-future forward outputs, device-side barrier ordering, on-device page tables with no per-step host sync, and a two-step-back confidence relay over the same channel — about 1.5x tighter than with the scheduler off and no bubble between `run_batch` iterations or draft-generate and verify phases.

Headline small-batch number is 383.7 tok/s at accept length ~5 at batch 1 on DeepSeek-V4-Pro, TP=8, B300[^dspark-sglang].

## Deployment pointers

Launch selects `--speculative-algorithm DSPARK` with a DSpark model such as `deepseek-ai/DeepSeek-V4-Flash-DSpark`, plus `--speculative-dspark-sps-table-path sps_table.json` for SPS-guided `compact`; `--disable-radix-cache` avoids bench cache hits in the reported sweeps[^dspark-sglang]. The prebuilt image is `lmsysorg/sglang:dev-dspark` pinned at commit `692c5f7d`; the source appendix gives full Figure 1/3/6 frontier-server, Figure 4 mixed-traffic, and Figure 5 B300/TP8 overlap-trace commands[^dspark-sglang].

A long-context checkpoint example is [Kimi K3 DSpark Speculator](kimi-k3-dspark.md): `RadixArk/Kimi-K3-DSpark` for `moonshotai/Kimi-K3` with block size 7, YaRN-16 1M serving context, and source-reported `acc_len` around 3–5.5 on short-context suites and 4.2553 on 1M-token RULER V2[^kimi-k3-dspark].

A dense-27B checkpoint example is [Qwen3.8-27B DSpark Speculator](qwen3.8-dspark.md): `RadixArk/Qwen3.8-27B-DSpark` for Qwen3.8-27B targets with five 5120-hidden layers, VanillaMarkov rank-256 head, gamma 7 and verify width 8, v2 acceptance +26.00% request-weighted and +26.45% workload-macro over v1, and up to 3.16x autoregressive throughput at concurrency 1 on the reported FP8 setup[^qwen38-dspark].

Roadmap items are a stronger online/adaptive cost model and scheduler, more dense/sparse model coverage, broader parallelism and topology coverage, productionized block-accept and calibration metrics, and hardening of the full-CUDA-graph path with stress/regression testing[^dspark-sglang].

## Relationships

- Uses [SGLang Speculative Decoding](sglang-speculative-decoding.md) — base EAGLE/MTP speculation surface; DSpark is the confidence-scheduled block-drafting alternative.
- Related to [SGLang DFlash Speculative Decoding](sglang-dflash-speculative-decoding.md) — both draft a whole block per forward, but DFlash uses block diffusion with KV injection while DSpark uses semi-autoregressive drafting with confidence-trimmed verify.
- Related to [vLLM Adaptive Verification for Speculative Decoding](vllm-adaptive-verification.md) — vLLM's survival-probability slot selection under a global cost-model budget versus SGLang's per-request SPS-argmax window; both currently need a DSpark confidence head.
- Related to [SGLang DeepSeek-V4 Inference](sglang-deepseek-v4-inference.md) — DeepSeek-V4-Flash/Pro DSpark checkpoints and sparse-MLA varlen verify run on the hybrid sparse-attention stack described there.
- Uses [SGLang Observability](sglang-observability.md) — cap-accept ceiling, per-request confidence, ECE, and block-accept estimator extend the metrics surface there.
- Uses [SGLang Server Arguments](sglang-server-arguments.md) — canonical reference for the launch, parallelism, memory, and DP-attention flags used in DSpark commands.
- Related to [Kimi K3 DSpark Speculator](kimi-k3-dspark.md) — long-context DSpark checkpoint extending the DFlash backbone with Markov logit-bias and confidence heads.
- Related to [Qwen3.8-27B DSpark Speculator](qwen3.8-dspark.md) — dense-27B DSpark checkpoint with v1/v2 acceptance and AR/EAGLE/DSpark throughput comparisons.

## Coverage limits

- Seven source attachments under `raw/2026-07-06-dspark-sglang/assets/` were enumerated but not pixel-verified; numeric claims above come from source prose, captions, and chart annotations for throughput/latency frontiers, ragged packing, dynamic-schedule, mixed-traffic, ZOS traces, and SPS fits[^dspark-sglang].
- The DSpark paper, SGLang PR `#30261` diff, roadmap issue `#30344`, Docker image contents, `frontier_prompt.txt`, Hugging Face DSpark checkpoints, and full benchmark harnesses were not inspected beyond the source's description; training steps and exact harness detail beyond the summary above are not compiled here[^dspark-sglang].
- Concurrency-1 versus high-batch trade-offs, window sizes, utilization ratios, and launch flags are workload-specific optima from the reported H200/B300 DeepSeek-V4 setups, not universal defaults[^dspark-sglang].

[^dspark-sglang]: DSpark in SGLang: Speculative Decoding with Confidence-Driven, Variable-Length Verification — `../raw/2026-07-06-dspark-sglang/index.md`.
[^kimi-k3-dspark]: Kimi K3 DSpark speculator — `../raw/Kimi-K3-DSpark.md`.
[^qwen38-dspark]: Qwen3.8-27B-DSpark — `../raw/Qwen3.8-27B-DSpark.md`.
