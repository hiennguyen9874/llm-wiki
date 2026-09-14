---
type: Concept
title: vLLM Draft-Model Speculative Decoding
description: Separate small draft model proposing num_speculative_tokens per step for target verification, with optional heterogeneous-vocab Token-Level Intersection.
tags: [vllm, speculative-decoding, draft-model]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:30:00Z }
sources:
  - id: draft-model
    resource: ../raw/vllm/features/speculative_decoding/draft_model.md
    title: Draft Models
---

vLLM `draft_model` speculative decoding uses a separate smaller draft model to propose `num_speculative_tokens` per step for the target model to verify, configured through `speculative_config` with `method: draft_model` in both offline and online serving[^draft-model].

## Configuration

Offline (`LLM` class)[^draft-model]:

```python
llm = LLM(
    model="Qwen/Qwen3-8B",
    speculative_config={
        "model": "Qwen/Qwen3-0.6B",
        "num_speculative_tokens": 5,
        "method": "draft_model",
    },
)
```

Online (`vllm serve`)[^draft-model]:

```bash
vllm serve Qwen/Qwen3-4B-Thinking-2507 \
  --speculative-config '{"model": "Qwen/Qwen3-0.6B", "num_speculative_tokens": 5, "method": "draft_model"}'
```

The client request path is unchanged; the OpenAI-compatible completions client works against the speculative server without modification[^draft-model].

## Heterogeneous vocabularies

By default draft and target models must share the same vocabulary[^draft-model].

Setting `use_heterogeneous_vocab: true` enables the Token-Level Intersection (TLI) algorithm, allowing a draft model from a different family with a different tokenizer[^draft-model]:

```python
llm = LLM(
    model="Qwen/Qwen3-8B",
    speculative_config={
        "method": "draft_model",
        "model": "HuggingFaceTB/SmolLM2-135M-Instruct",
        "num_speculative_tokens": 3,
        "use_heterogeneous_vocab": True,
    },
)
```

`use_heterogeneous_vocab` currently requires `draft_sample_method='greedy'` (the default); probabilistic draft sampling is not yet supported[^draft-model].

## Config surface

Set all speculative-decoding options through `--speculative-config` / `speculative_config`. The older split flags (`--speculative-model`, `--num-speculative-tokens`, and related per-key flags) are deprecated[^draft-model].

> Coverage limit: the source points to a `--speculative-config` schema in `README.md#--speculative-config-schema`; that schema file was not present in `raw/` and was not inspected, so supported keys beyond `model`, `num_speculative_tokens`, `method`, `use_heterogeneous_vocab`, and `draft_sample_method` are not compiled here.

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — `draft_model` speculation is configured on the offline `LLM` class or the online `vllm serve` server without changing the client request path.

[^draft-model]: Draft Models — `../raw/vllm/features/speculative_decoding/draft_model.md`, offline `LLM` and online `vllm serve` `draft_model` configuration, unchanged OpenAI-compatible client, same-vocab default with `use_heterogeneous_vocab` TLI option and greedy-sampling limit, and `--speculative-config` versus deprecated split-flag guidance.
