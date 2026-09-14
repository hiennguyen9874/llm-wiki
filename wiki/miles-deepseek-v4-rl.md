---
type: Concept
title: Miles DeepSeek-V4 Verified RL
description: Day-0 verified RL training for DeepSeek-V4 with full DP/TP/SP/EP/PP/CP parallelism, TileLang kernels, FP8 rollout and training, attention QAT, routing replay, and deterministic precision controls.
tags: [miles, deepseek-v4, rl, megatron, parallelism, fp8, qat, determinism]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:59:16Z }
sources:
  - id: dsv4-rl
    resource: ../raw/2026-04-25-deepseek-v4/index.md
    title: 'DeepSeek-V4 on Day 0: From Fast Inference to Verified RL with SGLang and Miles'
---

Miles with SGLang forms the first open-source stack to train DeepSeek-V4 on launch day, pairing rollout/training efficiency with verified numerical stability on the new hybrid sparse-attention plus mHC architecture[^dsv4-rl].

## Training backend

Most ops are rebuilt for the new architecture in Megatron-LM — complex compressed attention, new sparse-MLA and indexer modules, and the mHC layer[^dsv4-rl].

## Parallelism

All six Megatron strategies (DP/TP/SP/EP/PP/CP) are supported[^dsv4-rl].

- **TP and SP** are implemented across the compressed-attention module[^dsv4-rl].
- **PP**: mHC's four streams must survive stage boundaries so the receiving stage can mix them at every sublayer — `[seq, batch, hc_mult, hidden]` is carried across p2p instead of the usual 3-D tensor[^dsv4-rl].
- **CP**: all-gather CP on compressed attention; the C4 compressor's overlap transform shifts half of each compression group one position back along the sequence (adjacent groups share context at no extra KV cost), so under CP the shift crosses rank boundaries — a halo exchange would fix the overlap alone, but the downstream indexer top-k needs every compressed position anyway, so both collectives fold into a single all-gather (e.g. CP=4 on 1024 tokens: each rank holds 256 tokens, all-gather the full compressed tensor, apply overlap on the assembled sequence, slice back the local view); C128 layers have no overlap transform and skip the all-gather entirely[^dsv4-rl].

## Kernels

Built by adopting and extending Slime's GLM-5 kernel support for DeepSeek-V4[^dsv4-rl]:

- TileLang DSA indexer kernels adapted to the DSv4 indexer architecture for the lightning indexer[^dsv4-rl].
- Sparse-MLA TileLang kernel extended with per-head learnable attention-sink logits in the softmax denominator for core attention[^dsv4-rl].
- Fused TileLang Sinkhorn kernel for mHC[^dsv4-rl].

## RL features

- **FP8 rollout; FP8/BF16 training.** FP8 rollout plus BF16 and FP8 training, with the quantization processor in the weight update[^dsv4-rl].
- **Attention QAT.** Simulates FP8 activation quantization on rollout-in-FP8 paths (compressor KV, vanilla KV, indexer query) for kernel-level numerical match with SGLang at FP8 rollout precision[^dsv4-rl].
- **Rollout Routing Replay (R3).** Extends the R3 processor and TIS/MIS loss to `(b, s, h, d)` format for DeepSeek-V4 backends[^dsv4-rl].
- **Indexer replay (experimental).** DeepSeek-V4 has a second stochastic operator beyond MoE routing — the DSA indexer top-k over compressed KV; rollout top-k is captured in SGLang's compressed-attention backend, transported on the existing rollout channel, and re-injected per C4 layer at training — pipeline passes short-context correctness checks but is not verified end-to-end[^dsv4-rl].

## Numerical precision and stability

- FP32 precision is maintained for sensitive master weights and gradients across training, checkpoint conversion, and weight update[^dsv4-rl].
- Only the compressor backward all-reduce switches to FP32: it is a softmax-weighted sum over a long axis where the smallest summands matter, and BF16 rounding accumulated across TP ranks biases the sum toward the largest-magnitude contributor[^dsv4-rl].
- Selectively frozen unstable paths: Sinkhorn in mHC (as a mixing oracle), MoE router gate, per-expert score-correction bias, and hash-routed early layers[^dsv4-rl].
- Deterministic pins to avoid random KL-loss spikes: cuDNN deterministic, NCCL to Ring, TransformerEngine off nondeterministic paths, cuBLAS to a fixed workspace — at ~10–15% throughput cost[^dsv4-rl].
- Megatron fixes: checkpoint precision in distributed-optimizer under mixed FP32/BF16 groups, and CPU allocation of optimizer state during load to avoid resume-checkpoint OOM peaks[^dsv4-rl].

## Training result

A 285B-model run on DAPO at 4096 max response length, on 32 GB300 GPUs with TP/SP/EP/PP parallelism, FP8 rollout + BF16 training, and R3 enabled: rollout/training log-prob drift ~0.023 at the first step (Step-0 train-inference diff ~0.02–0.03), with rollout raw reward and AIME eval accuracy (4096 max-len truncated) growing steadily[^dsv4-rl].

Hardware support covers Hopper, Blackwell, and Grace Blackwell[^dsv4-rl].

## Relationships

- Uses [SGLang for RL Systems](sglang-for-rl.md) — SGLang rollout, weight-refit, pause/continue, deterministic-inference, and gateway surface that the Miles Day-0 pipeline pairs with for verified RL.
- Uses [SGLang Deterministic Inference](sglang-deterministic-inference.md) — deterministic rollout side of the Step-0 train-inference diff and attention-QAT numerical match.
- Related to [SGLang DeepSeek-V4 Inference](sglang-deepseek-v4-inference.md) — inference-side Day-0 companion (ShadowRadix, spec/MTP, HiSparse, kernels, parallelism) sharing the same source and hardware coverage.
- Related to [vLLM Sleep Mode](vllm-sleep-mode.md) — vLLM counterpart for levelled sleep/wake and partial restore in colocated rollout/training.
- Related to [Miles DeepSeek-V4.1 Verified RL](miles-deepseek-v41-rl.md) — V4.1 successor with shared compressed plus window state, FP4/FP8 QAT, recomputed indexer top-k, and colocated 16-GPU DAPO validation.

## Coverage limits

- Miles reward/eval curves and the Day-0 RL pipeline diagram were taken from prose and captions without pixel-level verification; no step counts, absolute scores, or variance bands beyond the drift and growth trends above were compiled[^dsv4-rl].
- Slime GLM-5 kernels, DAPO task setup, TIS/MIS loss definitions, and the Miles/SGLang roadmap issues were not inspected[^dsv4-rl].
- Indexer replay is explicitly experimental with short-context correctness only; it is not an end-to-end verified procedure[^dsv4-rl].

[^dsv4-rl]: DeepSeek-V4 on Day 0: From Fast Inference to Verified RL with SGLang and Miles — `../raw/2026-04-25-deepseek-v4/index.md`, covering Megatron modeling rebuild, DP/TP/SP/EP/PP/CP support with mHC p2p and C4 all-gather detail, TileLang kernels, FP8 rollout/training with attention QAT, R3 and experimental indexer replay, FP32/deterministic stability controls, DAPO training result, and hardware support.
