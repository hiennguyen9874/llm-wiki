---
type: Concept
title: vLLM Suffix Speculative Decoding
description: Draft-free speculative decoding that proposes adaptive continuations from prompt and generation suffix matches via method suffix with Arctic Inference.
tags: [vllm, speculative-decoding, suffix]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:39:33Z }
sources:
  - id: suffix
    resource: ../raw/vllm/features/speculative_decoding/suffix.md
    title: Suffix Decoding
---

vLLM runs suffix speculative decoding by generating draft tokens from suffix pattern matches rather than from a separate draft model, selected through `speculative_config` with `method: suffix`[^suffix].

## How it differs from n-gram

Like n-gram, suffix decoding pattern-matches using the last `n` generated tokens[^suffix]. Unlike n-gram, it (1) matches against both the prompt and previous generations, (2) uses frequency counts to propose the most likely continuations, and (3) speculates an adaptive per-request, per-iteration token count for better acceptance rates[^suffix].

Best fit is high-repetition work such as code editing, agentic loops such as self-reflection and self-consistency, and RL rollouts[^suffix].

## Configuration

Requires [Arctic Inference](https://github.com/snowflakedb/ArcticInference), installed with `pip install arctic-inference`[^suffix].

Because the speculative count is dynamic, `num_speculative_tokens` is the maximum per step; the source suggests a high value such as `16` or `32` (default)[^suffix].

Offline (`LLM` class)[^suffix]:

```python
from vllm import LLM, SamplingParams

prompts = ["The future of AI is"]
sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

llm = LLM(
    model="Qwen/Qwen3-8B",
    tensor_parallel_size=1,
    speculative_config={
        "method": "suffix",
        "num_speculative_tokens": 32,
    },
)
outputs = llm.generate(prompts, sampling_params)
```

The example leaves the sampling path unchanged through `SamplingParams` and `llm.generate`, and unlike draft-model methods carries no separate draft `model` field[^suffix].

> Coverage limit: the source is a short offline example plus a pointer to the suffix-decoding technical report; that report was not inspected, and the source does not define online `vllm serve` flags or model compatibility, so those are not compiled here.

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — suffix speculation is configured on the offline `LLM` class through `speculative_config` without changing the `generate` call.
- Related to [vLLM N-Gram Speculative Decoding](vllm-ngram-speculative-decoding.md) — `ngram` proposes from prompt n-grams with fixed `num_speculative_tokens` and `prompt_lookup_max`, while `suffix` matches prompt plus generations with frequency-ranked, adaptive-length proposals.
- Related to [vLLM Draft-Model Speculative Decoding](vllm-draft-model.md) — `draft_model` pairs a separate small proposer with the target, while `suffix` derives proposals from suffix matches with no draft `model` field.
- Related to [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — MTP is the native multi-token-prediction alternative that also avoids a separate draft model.

[^suffix]: Suffix Decoding — `../raw/vllm/features/speculative_decoding/suffix.md`, draft-free `method: suffix` property, prompt-plus-generation matching with frequency counts and adaptive speculation, high-repetition workloads, Arctic Inference dependency, `num_speculative_tokens` as maximum with `16`/`32` guidance, and offline `LLM` example with `Qwen/Qwen3-8B`.
