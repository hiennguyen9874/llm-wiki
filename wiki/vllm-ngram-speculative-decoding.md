---
type: Concept
title: vLLM N-Gram Speculative Decoding
description: Draft-free speculative decoding that proposes tokens by matching n-grams in the prompt via method ngram with num_speculative_tokens and prompt_lookup_max.
tags: [vllm, speculative-decoding, ngram]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T15:00:00Z }
sources:
  - id: ngram
    resource: ../raw/vllm/features/speculative_decoding/n_gram.md
    title: N-Gram Speculation
---

vLLM runs n-gram speculative decoding by generating proposals from n-grams matched in the prompt rather than from a separate draft model, selected through `speculative_config` with `method: ngram`[^ngram].

## Configuration

Offline (`LLM` class)[^ngram]:

```python
from vllm import LLM, SamplingParams

prompts = ["The future of AI is"]
sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

llm = LLM(
    model="Qwen/Qwen3-8B",
    tensor_parallel_size=1,
    speculative_config={
        "method": "ngram",
        "num_speculative_tokens": 5,
        "prompt_lookup_max": 4,
    },
)
outputs = llm.generate(prompts, sampling_params)
```

The example proposes `num_speculative_tokens: 5` per step with `prompt_lookup_max: 4`, and leaves the sampling path unchanged through `SamplingParams` and `llm.generate`[^ngram]. Unlike draft-model methods, the example config carries no separate draft `model` field[^ngram].

> Coverage limit: the source is a short offline example plus a pointer to an X thread on n-gram speculation; that thread was not inspected, and the source does not define `prompt_lookup_max` semantics, online `vllm serve` flags, or model compatibility, so those are not compiled here.

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — n-gram speculation is configured on the offline `LLM` class through `speculative_config` without changing the `generate` call.
- Related to [vLLM Draft-Model Speculative Decoding](vllm-draft-model.md) — `draft_model` pairs a separate small proposer with the target, while `ngram` derives proposals from prompt n-grams with no draft `model` field.
- Related to [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — EAGLE is the separate-speculator alternative when prompt matching is insufficient.
- Related to [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — MTP is the native multi-token-prediction alternative that also avoids a separate draft model.

[^ngram]: N-Gram Speculation — `../raw/vllm/features/speculative_decoding/n_gram.md`, prompt n-gram proposal property, offline `LLM` example with `method: ngram`, `num_speculative_tokens: 5`, `prompt_lookup_max: 4`, `Qwen/Qwen3-8B` target, and unchanged `SamplingParams`/`generate` path.
