---
type: Concept
title: vLLM MTP Speculative Decoding
description: Native multi-token prediction speculation via method mtp with no separate draft model, including Gemma 4 assistant-checkpoint support and shared-KV wiring.
tags: [vllm, speculative-decoding, mtp]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T14:00:00Z }
sources:
  - id: mtp
    resource: ../raw/vllm/features/speculative_decoding/mtp.md
    title: MTP (Multi-Token Prediction)
---

vLLM runs MTP speculative decoding when the target model includes native multi-token prediction capability, so no separate draft model is needed; it is selected through `speculative_config` with `method: mtp` and is useful for MTP-capable models wanting model-based speculation with minimal extra configuration[^mtp].

## Configuration

Offline (`LLM` class)[^mtp]:

```python
llm = LLM(
    model="XiaomiMiMo/MiMo-7B-Base",
    tensor_parallel_size=1,
    speculative_config={
        "method": "mtp",
        "num_speculative_tokens": 1,
    },
)
```

Online (`vllm serve`)[^mtp]:

```bash
vllm serve XiaomiMiMo/MiMo-7B-Base \
    --tensor-parallel-size 1 \
    --speculative-config '{"method":"mtp","num_speculative_tokens":1}'
```

MTP only works for model families that support MTP in vLLM; `num_speculative_tokens` controls speculative depth, with a small value like `1` as a good starting default[^mtp]. If the model does not support MTP, use another method such as EAGLE or draft-model speculation[^mtp].

## Gemma 4 assistant checkpoints

Gemma 4 assistant checkpoints use vLLM's Gemma 4 MTP path and are not generic draft models, even though they are passed through the `model` field in `--speculative-config`[^mtp]:

```bash
vllm serve google/gemma-4-E2B-it \
    --tensor-parallel-size 1 \
    --max-model-len 8192 \
    --speculative-config '{"method":"mtp","model":"gg-hf-am/gemma-4-E2B-it-assistant","num_speculative_tokens":1}'
```

The E2B, E4B, 12B, 26B-A4B, and 31B Gemma 4 IT assistant checkpoints are supported[^mtp]. Tower-based variants use `model_type: gemma4_assistant` and the encoder-free Gemma 4 Unified variant (12B) uses `model_type: gemma4_unified_assistant`; vLLM maps both to `Gemma4MTPModel` internally and wires the assistant layers to share KV cache with the target model[^mtp].

If an older vLLM release logs `SpeculativeConfig(method='draft_model', ...)` for a Gemma 4 assistant checkpoint, that release is treating the assistant as a generic draft model and may fail during initialization for multimodal Gemma 4 targets; upgrade to a version with Gemma 4 MTP support instead[^mtp].

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — MTP speculation is configured on the offline `LLM` class or the online `vllm serve` server through `speculative_config`.
- Related to [vLLM Draft-Model Speculative Decoding](vllm-draft-model.md) — MTP needs no separate draft model, while `draft_model` pairs a small proposer with the target; Gemma 4 assistants must use `method: mtp`, not generic draft-model handling.
- Related to [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — EAGLE is the separate-speculator alternative named in the source when the model lacks MTP support.
- Related to [vLLM MLP Speculative Decoding](vllm-mlp-speculative-decoding.md) — MLP speculators are another separate-draft alternative when native MTP is unavailable.

[^mtp]: MTP (Multi-Token Prediction) — `../raw/vllm/features/speculative_decoding/mtp.md`, native-MTP `method: mtp` definition and no-draft-model property, MiMo offline/online `num_speculative_tokens: 1` examples, Gemma 4 assistant `Gemma4MTPModel` path with supported IT checkpoints and shared-KV wiring, older-release `draft_model` misclassification warning, and MTP-support plus EAGLE/draft-model fallback notes.
