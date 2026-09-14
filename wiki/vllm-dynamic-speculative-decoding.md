---
type: Concept
title: vLLM Dynamic Speculative Decoding
description: Batch-size-dependent draft-token table that lowers K as concurrency rises to preserve decode speed.
tags: [vllm, speculative-decoding, dynamic]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:32:41Z }
sources:
  - id: dynamic-sd
    resource: ../raw/vllm/features/speculative_decoding/dynamic_speculative_decoding.md
    title: Dynamic Speculative Decoding
---

vLLM Dynamic Speculative Decoding tunes the number of draft tokens `K` to current concurrency through a `num_speculative_tokens_per_batch_size` batch-range table, so the same deployment keeps speculative-decoding gains at low load and reduces or disables drafting before verification cost hurts time-per-output-token at high load[^dynamic-sd].

## Why static K fails

Speculative-decoding methods verify `K` tokens per sequence during decoding, making the effective batch size `BS*K` and raising verification compute[^dynamic-sd].

When `BS*K` passes a critical batch size, speculative decoding slows decode speed (TPOT); Dynamic SD keeps the benefit by tuning `K` to an optimal value for the current concurrency[^dynamic-sd].

## Configuration

Add `num_speculative_tokens_per_batch_size` to the config of a speculative-decoding method as a list of `[start_bs, end_bs, optimal_K]` ranges; when concurrency falls in `[start_bs, end_bs]`, `optimal_K` draft tokens are used[^dynamic-sd]:

```bash
--speculative-config '{
    "method": "eagle",
    "model": "yuhuili/EAGLE-LLaMA3.1-Instruct-8B",
    "num_speculative_tokens": 3,
    "num_speculative_tokens_per_batch_size": [
      [1, 64, 3],
      [65, 128, 1],
      [129, 512, 0]
    ]
  }'
```

This example uses `K=3` for concurrency 1–64, `K=1` for 65–128, and `K=0` (no draft tokens) for 129–512[^dynamic-sd].

## Use cases

- Variable-concurrency workload on one deployment: `K` decreases as concurrency increases[^dynamic-sd].
- RL rollout that starts with high batch size but ends with a small batch of long-tail requests generating many tokens and stalling rollout progress: `K` rises again at the end of the rollout[^dynamic-sd].

## Tested methods and examples

Tested with Eagle, Eagle-3, and DFlash; other speculative-decoding methods may or may not work out of the box[^dynamic-sd].

Eagle example[^dynamic-sd]:

```bash
VLLM_USE_V2_MODEL_RUNNER=0 vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --speculative-config '{
    "method": "eagle",
    "model": "yuhuili/EAGLE-LLaMA3.1-Instruct-8B",
    "num_speculative_tokens": 3,
    "num_speculative_tokens_per_batch_size": [
      [1, 64, 3],
      [65, 128, 1],
      [129, 512, 0]
    ]
  }'
```

Eagle3 example with a finer high-load ramp[^dynamic-sd]:

```bash
VLLM_USE_V2_MODEL_RUNNER=0 vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --speculative-config '{
    "method": "eagle3",
    "model": "yuhuili/EAGLE3-LLaMA3.1-Instruct-8B",
    "num_speculative_tokens": 3,
    "num_speculative_tokens_per_batch_size": [
      [1, 16, 5],
      [17, 32, 4],
      [33, 64, 3],
      [65, 128, 1],
      [129, 512, 0]
    ]
  }'
```

## Limitations

- Full CUDA graphs only work with Model Runner V2; Model Runner V1 supports only piece-wise CUDA graphs with this feature[^dynamic-sd].
- Not compatible with data parallelism (`--data-parallel-size > 1`): each DP rank schedules independently and can pick a different `K`, causing DP collective divergence and deadlocks; when DP is enabled, vLLM automatically disables `num_speculative_tokens_per_batch_size` and falls back to the static `num_speculative_tokens` value[^dynamic-sd].

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — configured through `vllm serve --speculative-config`.
- Uses [vLLM Model Runner V2](vllm-model-runner-v2.md) — required for full CUDA-graph support with Dynamic SD; Model Runner V1 is limited to piece-wise graphs.
- Uses [vLLM CUDA Graphs Modes and Dispatch](vllm-cuda-graphs.md) — CUDA-graph mode coverage differs by model runner when Dynamic SD is active.
- Uses [vLLM Data Parallel Deployment](vllm-data-parallel-deployment.md) — incompatible with data parallelism because independent per-rank `K` choices diverge collectives; vLLM falls back to static `K`.
- Related to [vLLM Adaptive Verification for Speculative Decoding](vllm-adaptive-verification.md) — both address load-dependent draft sizing, but Dynamic SD uses a configured batch-size-to-`K` table while adaptive verification budgets per-step draft slots by survival probability and profiled cost.

[^dynamic-sd]: Dynamic Speculative Decoding — `../raw/vllm/features/speculative_decoding/dynamic_speculative_decoding.md`, covering `BS*K` verification cost and TPOT crossover, `num_speculative_tokens_per_batch_size` range schema, variable-concurrency and RL-rollout use cases, Eagle/Eagle3 online examples, and Eagle/Eagle-3/DFlash, CUDA-graph/runner, and data-parallel limits.
