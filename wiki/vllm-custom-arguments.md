---
type: Concept
title: vLLM Custom Arguments
description: Passing out-of-spec SamplingParams and REST arguments via SamplingParams.extra_args and vllm_xargs for offline and online inference.
tags: [vllm, sampling, api]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:05:35Z }
sources:
  - id: custom-arguments
    resource: ../raw/vllm/features/custom_arguments.md
    title: Custom Arguments
---

vLLM custom arguments pass request-scoped arguments outside the `SamplingParams` and REST API specifications as a dictionary, so adding or removing one does not require recompiling vLLM[^custom-arguments].

The canonical use case is configuring a custom logits processor without modifying vLLM source code[^custom-arguments].

## Offline path

Pass a dict to `SamplingParams.extra_args`, visible to any code with access to `SamplingParams`[^custom-arguments]:

```python
SamplingParams(extra_args={"your_custom_arg_name": 67})
```

This carries non-`SamplingParams` arguments into the offline `LLM` as part of a request[^custom-arguments].

## Online path

The OpenAI-compatible REST API and the Anthropic-compatible `/v1/messages` endpoint accept custom arguments via `vllm_xargs`[^custom-arguments]:

```bash
curl http://localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen2.5-1.5B-Instruct",
        "vllm_xargs": {"your_custom_arg": 67}
    }'
```

OpenAI SDK users pass the same field through `extra_body`[^custom-arguments]:

```python
batch = await client.completions.create(
    model="Qwen/Qwen2.5-1.5B-Instruct",
    extra_body={
        "vllm_xargs": {
            "your_custom_arg": 67
        }
    }
)
```

## Offline/online equivalence

`vllm_xargs` is assigned to `SamplingParams.extra_args` under the hood, so code written against `SamplingParams.extra_args` works in both offline and online scenarios[^custom-arguments].

## Validation requirement

Custom logits processors consuming these arguments must implement `validate_params` for them; otherwise invalid custom arguments can cause unexpected behaviour[^custom-arguments].

## Coverage limits

- The custom-logits-processor guide is now compiled in [vLLM Custom Logits Processors](vllm-custom-logits-processors.md); this concept keeps only the argument-transport role[^custom-arguments].
- Endpoint coverage is as stated in the source (OpenAI-compatible REST plus Anthropic-compatible `/v1/messages`); other servers/endpoints were not verified.

## Relationships

- Uses [vLLM Logits Processors](vllm-logits-processors.md) — custom arguments are the out-of-spec channel for per-request processor configuration, validated by `validate_params`.
- Uses [vLLM Custom Logits Processors](vllm-custom-logits-processors.md) — worked `target_token` configuration, `validate_params` enforcement, and loading/invocation paths for the motivating processor use case.
- Uses [vLLM Entrypoints](vllm-entrypoints.md) — the offline `LLM` path uses `SamplingParams.extra_args` while the online server path uses `vllm_xargs`.

[^custom-arguments]: Custom Arguments — `../raw/vllm/features/custom_arguments.md`, covering dict-passed out-of-spec arguments, offline `SamplingParams.extra_args`, online `vllm_xargs` for OpenAI-compatible and Anthropic-compatible endpoints, SDK `extra_body` usage, offline/online equivalence, and the `validate_params` requirement.
