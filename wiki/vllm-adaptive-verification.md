---
type: Concept
title: vLLM Adaptive Verification for Speculative Decoding
description: Per-step adaptive draft verification that budgets cross-request slots by survival probability and profiled step cost, currently for DSpark with a confidence head.
tags: [vllm, speculative-decoding, dspark]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:42:01Z }
sources:
  - id: adaptive-verification
    resource: ../raw/vllm/features/speculative_decoding/adaptive_verification.md
    title: Adaptive Verification
  - id: dspark-sglang
    resource: ../raw/2026-07-06-dspark-sglang/index.md
    title: "DSpark in SGLang: Speculative Decoding with Confidence-Driven, Variable-Length Verification"
---

vLLM adaptive verification replaces fixed full-block verification with per-step selection of draft slots under a startup-profiled global token budget to maximize expected accepted tokens per second, so one configuration holds across load without per-deployment `num_speculative_tokens` tuning; it is off by default and today only supported for DSpark with a confidence head[^adaptive-verification].

## Why static draft length fails

Speculative decoding trades fewer decode steps for more compute: at batch size 1 the GPU is memory-bound with spare compute so extra draft tokens are close to free, while at batch size 256 draft tokens compete with real tokens and rejected tokens waste throughput[^adaptive-verification].

Per-position acceptance decays fast, so a slot that is effectively free while memory-bound carries a real throughput cost once saturated; the crossover moves with load and workload-dependent acceptance rates, so no static `num_speculative_tokens` is right across concurrencies[^adaptive-verification].

## How selection and budgeting work

Adaptive verification decides per step how much of the draft to verify instead of verifying the full block for every request[^adaptive-verification]:

- Every `(request, position)` draft slot is scored by its survival probability, the running product of that request's per-position confidences[^adaptive-verification].
- The highest-scoring slots are admitted until a global budget is spent[^adaptive-verification].
- Slots compete across requests: position 5 of a confident request can outrank position 1 of a doubtful one, so one request keeps its full block while another is trimmed after a token or two[^adaptive-verification].

The budget comes from a cost model profiled at startup: vLLM measures what a step costs at each shape, then picks the token count that maximizes expected accepted tokens per second[^adaptive-verification].

## Support

Adaptive verification needs per-position acceptance estimates, so today it is only supported for DSpark with a confidence head[^adaptive-verification].

## Usage

It is off by default; enable it in the speculative config[^adaptive-verification]:

```bash
vllm serve deepseek-ai/DeepSeek-V4-Flash-DSpark \
  --tokenizer-mode deepseek_v4 --trust-remote-code \
  --speculative-config '{
    "method": "dspark",
    "model": "deepseek-ai/DeepSeek-V4-Flash-DSpark",
    "num_speculative_tokens": 7,
    "draft_sample_method": "probabilistic",
    "enable_adaptive_verification": true
  }'
```

Set `enable_adaptive_verification: false` to verify the full block for every request[^adaptive-verification].

## Requirements and limitations

- The attention backend must tolerate device-decided query lengths, since the CPU lengths only bound them from above; backends that plan off the CPU lengths are excluded by the attention selector, and rejected at startup for models that hard-wire their backend[^adaptive-verification].
- Full cudagraphs are required because step costs are profiled from captured graphs, so `--enforce-eager` is rejected at startup[^adaptive-verification].
- Not supported with LoRA because the per-token LoRA mapping is built from CPU-side boundaries, or with pipeline parallelism because cost curves and confidences exist only on the last rank[^adaptive-verification].

## Tuning the cost profile

Step costs are profiled against a synthetic KV context, 8192 tokens by default; deployments serving much longer contexts may want to raise it so the profiled step reads a more realistic amount of cache[^adaptive-verification]:

```bash
export VLLM_ADAPTIVE_VERIFICATION_PROFILE_CONTEXT_LEN=131072
```

This matters less for sparse-attention models like DeepSeek-V4 since the cheap indexer is the main cost that scales with context length[^adaptive-verification].

## Relationships

- Uses [vLLM Attention Backends](vllm-attention-backends.md) — adaptive verification requires a backend that tolerates device-decided query lengths; CPU-length-planned backends are excluded or rejected at startup.
- Uses [vLLM CUDA Graphs Modes and Dispatch](vllm-cuda-graphs.md) — full cudagraphs are required because the cost model is profiled from captured graphs; `--enforce-eager` is rejected.
- Uses [vLLM LoRA Adapters](vllm-lora-adapters.md) — unsupported with LoRA because per-token LoRA mapping is built from CPU-side boundaries.
- Uses [vLLM Tensor and Pipeline Parallel Scaling](vllm-parallelism-scaling.md) — unsupported with pipeline parallelism because cost curves and confidences exist only on the last rank.
- Uses [vLLM Entrypoints](vllm-entrypoints.md) — enabled through `vllm serve` speculative-config via `enable_adaptive_verification`.
- Related to [SGLang DSpark Speculative Decoding](sglang-dspark-speculative-decoding.md) — SGLang's per-request SPS-argmax window with ragged CUDA-graph verify and `static` / `compact` / `cap-accept` ceiling observability versus vLLM's global slot budget[^dspark-sglang].

[^adaptive-verification]: Adaptive Verification — `../raw/vllm/features/speculative_decoding/adaptive_verification.md`, covering load-dependent speculative tradeoff, survival-probability slot selection with global cost-model budget, DSpark confidence-head support, `enable_adaptive_verification` usage, attention/cudagraph/LoRA/pipeline-parallel limits, and `VLLM_ADAPTIVE_VERIFICATION_PROFILE_CONTEXT_LEN` tuning.
[^dspark-sglang]: DSpark in SGLang: Speculative Decoding with Confidence-Driven, Variable-Length Verification — `../raw/2026-07-06-dspark-sglang/index.md`.
