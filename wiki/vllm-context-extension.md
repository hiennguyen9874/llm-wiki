---
type: Concept
title: vLLM Context Extension via RoPE Scaling
description: Extending model context length with rope_parameters overrides via --hf-overrides and --max-model-len for offline and online inference.
tags: [vllm, rope, long-context, serving]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: context-ext
    resource: ../raw/vllm/features/context_extension.md
    title: Context Extension
---

vLLM extends model context length by overriding RoPE `rope_parameters` through `--hf-overrides` and sizing serving capacity with `--max-model-len`, replacing the removed `--rope-scaling` flag[^context-ext].

## Deprecated flag

- The older `--rope-scaling` parameter is no longer supported[^context-ext].
- Use the `--hf-overrides` method with `rope_parameters` instead[^context-ext].

## Offline inference

- An offline example script extends a Qwen model with the YARN method (`rope_parameters`) and runs a simple chat example[^context-ext].
- Usage is `python examples/features/context_extension/context_extension_offline.py`[^context-ext].

## Online serving

- Serve with extended context by passing a JSON `rope_parameters` override plus the enlarged `--max-model-len`[^context-ext].
- Example extends `Qwen/Qwen3-0.6B` from 32768 to 131072 tokens with `factor: 4.0`, `original_max_position_embeddings: 32768`, `rope_theta: 1000000`, and `rope_type: yarn`[^context-ext]:

```bash
vllm serve Qwen/Qwen3-0.6B \
  --hf-overrides '{"rope_parameters": {"factor": 4.0, "original_max_position_embeddings": 32768, "rope_theta": 1000000, "rope_type": "yarn"}}' \
  --max-model-len 131072
```

- After the server starts, it is queried through the OpenAI-compatible chat completions API pointed at the local server with the same model name[^context-ext].

## Key parameters

- Available `rope_parameters` fields depend on the chosen `rope_type`; full RoPE-type detail lives in the Hugging Face Transformers RoPE documentation[^context-ext].
- Common parameters include `rope_type` (e.g. `yarn`, `linear`, `dynamic`), `factor`, and `original_max_position_embeddings`[^context-ext].
- vLLM-specific: `--max-model-len` is the new maximum sequence length after extension (`original * factor`), used for KV-cache pre-allocation and as the request limit at serving time[^context-ext].

## Coverage limits

- The offline example script (`examples/features/context_extension/context_extension_offline.py`) was not present in `raw/` and was not inspected beyond the feature note's summary[^context-ext].
- The external Hugging Face Transformers RoPE documentation was not ingested[^context-ext].

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — context extension is exercised through both offline inference and `vllm serve` online serving.
- Uses [vLLM Hugging Face Integration](vllm-huggingface-integration.md) — `--hf-overrides` patches the loaded Hugging Face model config before architecture mapping.

[^context-ext]: Context Extension — `../raw/vllm/features/context_extension.md`.
