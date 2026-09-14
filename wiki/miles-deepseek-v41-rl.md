---
type: Concept
title: Miles DeepSeek-V4.1 Verified RL
description: Day-0 Miles plus SGLang RL for DeepSeek-V4.1 with shared-state parallelism, FP4 and FP8 quantization-aware training, routing replay, deterministic precision, and colocated rollout.
tags: [miles, deepseek-v4.1, rl, megatron, parallelism, qat, determinism]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:59:16Z }
sources:
  - id: dsv41-rl
    resource: ../raw/2026-09-10-deepseek-v41/index.md
    title: 'SGLang and Miles Add Day-0 Support for DeepSeek-V4.1'
---

Miles with SGLang trains DeepSeek-V4.1 on day 0 through a Megatron-Core plugin plus SGLang rollouts, with the central objective of minimizing trainer-versus-rollout log-probability differences on the same responses[^dsv41-rl].

## Parallelism and shared state

The backend supports DP, TP, SP, EP, PP, and CP. TP and SP partition attention projections and compressor groups[^dsv41-rl].

Pipeline boundaries carry all four mHC residual streams, predecessor mixing coefficients, and attention state still needed by downstream consumers; that state also lets recomputed layers recover inputs locally. Context parallelism keeps queries local while gathering window KV, compressed KV, and indexer keys across ranks for global sparse retrieval[^dsv41-rl].

## Quantization-aware training

The training forward reproduces the serving engine's FP4 rounding for compressed latents and indexer queries and keys, plus FP8 rounding for the window cache. Straight-through gradients allow optimization through these discrete ops. The window cache uses the engine's paged-cache kernels for forward values with a differentiable emulation carrying the gradient. Sparse attention and indexing reuse the DeepSeek-V4 plugin's TileLang kernels; RoPE and fake quantization follow the serving formulas[^dsv41-rl].

## Routing replay

Rollout Routing Replay feeds sampled expert assignments into the trainer's MoE layers, preventing routing ties from taking a different expert path. Indexer top-k is recomputed rather than stored and replayed: once its quantized inputs matched, replay added no measured parity benefit, so recomputation avoids retaining per-layer selections for every rollout token[^dsv41-rl].

## Numerical consistency

Compressor gates, normalization statistics, mHC mixing, Engram gating, and attention-sink accumulation use FP32 with casts at operation boundaries. The compressed-KV projection's gradient all-reduce also uses FP32. Deterministic reductions and matrix-multiplication settings make repeated forwards reproducible, helping separate execution variability from persistent trainer–rollout differences[^dsv41-rl].

## Colocated training and rollout

Training and rollout alternate on 16 GPUs. Optimizer moments stream to node-local NVMe, and trainer state is offloaded before rollout engines resume. Updated BF16 weights transfer in buckets after each training step. The frozen FP8 Engram tables use host-memory backing and are excluded from weight synchronization. The backend loads the Hugging Face checkpoint directly through its model bridge[^dsv41-rl].

## Validated run

Steps 0–80 of a DAPO run on DAPO-Math-17K with a 2K-token response cap ran on 16 GB300 GPUs with TP4, EP16, and 128 samples per step. First and last five-step mean rewards are 0.51 and 0.78. Over the plotted interval, per-token KL between trainer and rollout ranges from 0.0012 to 0.0017, and mean absolute log-probability gap ranges from 0.017 to 0.025 nats[^dsv41-rl].

The measured discrepancy stays small without sustained growth during this run, but these measurements do not isolate its cause or establish numerical equivalence. The run completed 120+ steps without a failure[^dsv41-rl].

## Relationships

- Related to [Miles DeepSeek-V4 Verified RL](miles-deepseek-v4-rl.md) — V4.1 keeps full DP/TP/SP/EP/PP/CP plus TileLang and FP8/QAT discipline while changing the modeled state to shared compressed plus window KV, mHC streams, and Engram, and switching indexer replay from experimental capture to recompute.
- Related to [SGLang DeepSeek-V4.1 Inference](sglang-deepseek-v41-inference.md) — inference-side day-0 companion covering V4.1 architecture, shared KV and selection, Engram host offload, bounded replay, and kernel execution.
- Uses [SGLang for RL Systems](sglang-for-rl.md) — SGLang rollout, weight-refit, pause/continue, deterministic-inference, and gateway surface that the colocated BF16-weight bucket transfer pairs with.
- Uses [SGLang Deterministic Inference](sglang-deterministic-inference.md) — deterministic rollout side of the trainer-versus-rollout KL and log-prob gap measurements.
- Depends on [SGLang Attention Backends](sglang-attention-backends.md) — sparse-attention execution context for window plus compressed plus indexer-key gathering under CP.

## Coverage limits

- Reward and trainer-versus-rollout mismatch curves were inspected as a rendered image with numeric ranges taken from prose; no per-step table beyond the quoted reward, KL, and log-prob ranges was compiled[^dsv41-rl].
- DAPO task setup, GRPO/loss details, bucket-transfer sizing, NVMe streaming throughput, and model-bridge internals beyond the claims above were not inspected[^dsv41-rl].
- Small, non-growing discrepancy over 80 plotted steps is an observed run result, not proof of equivalence or of long-run stability[^dsv41-rl].

[^dsv41-rl]: SGLang and Miles Add Day-0 Support for DeepSeek-V4.1 — `../raw/2026-09-10-deepseek-v41/index.md`, covering Megatron shared-state DP/TP/SP/EP/PP/CP support, FP4/FP8 quantization-aware training, routing versus indexer replay, FP32/deterministic precision controls, colocated 16-GPU rollout with host-backed Engram, and the DAPO-Math-17K validated run.
