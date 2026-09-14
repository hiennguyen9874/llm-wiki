---
type: Concept
title: vLLM Parallel Draft Model Speculative Decoding
description: Parallel draft-model speculation pairing a target model with a PARD draft model via method draft_model plus parallel_drafting, with offline and online configuration.
tags: [vllm, speculative-decoding, pard]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T15:30:00Z }
sources:
  - id: parallel-draft
    resource: ../raw/vllm/features/speculative_decoding/parallel_draft_model.md
    title: Parallel Draft Models
---

vLLM runs parallel draft-model speculation by pairing a target model with a PARD (Parallel Draft Models) draft proposer, configured as `method: draft_model` with `parallel_drafting: true` in `speculative_config`[^parallel-draft].

## Configuration

Offline (`LLM` class)[^parallel-draft]:

```python
from vllm import LLM, SamplingParams

prompts = ["The future of AI is"]
sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

llm = LLM(
    model="Qwen/Qwen3-8B",
    tensor_parallel_size=1,
    speculative_config={
        "model": "amd/PARD-Qwen3-0.6B",
        "num_speculative_tokens": 12,
        "method": "draft_model",
        "parallel_drafting": True,
    },
)
outputs = llm.generate(prompts, sampling_params)
```

Online (`vllm serve`)[^parallel-draft]:

```bash
vllm serve Qwen/Qwen3-4B \
    --host 0.0.0.0 \
    --port 8000 \
    --seed 42 \
    -tp 1 \
    --max-model-len 2048 \
    --gpu-memory-utilization 0.8 \
    --speculative-config '{"model": "amd/PARD-Qwen3-0.6B", "num_speculative_tokens": 12, "method": "draft_model", "parallel_drafting": true}'
```

The examples use `Qwen/Qwen3-8B` offline and `Qwen/Qwen3-4B` online as targets, `amd/PARD-Qwen3-0.6B` as the draft model, and propose `num_speculative_tokens: 12` per step[^parallel-draft].

## Pretrained weights

Pre-trained PARD weights are published in the `amd/pard` Hugging Face collection[^parallel-draft].

> Coverage limit: the source names PARD and links its paper and weight collection, but does not define `parallel_drafting` semantics, acceptance behavior, performance, compatibility, or target/draft pairing constraints beyond the two examples; the linked paper and Hugging Face collection were not inspected, so those details are not compiled here.

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — parallel drafting is configured on the offline `LLM` class or the online `vllm serve` server through `speculative_config`.
- Related to [vLLM Draft-Model Speculative Decoding](vllm-draft-model.md) — parallel drafting is a `method: draft_model` variant that adds `parallel_drafting: true` with a PARD proposer instead of a standard small draft model.
- Related to [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — EAGLE is the separate-speculator alternative when a PARD draft model is not used.
- Related to [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — MTP is the native multi-token-prediction alternative that avoids a separate draft model.
- Related to [vLLM N-Gram Speculative Decoding](vllm-ngram-speculative-decoding.md) — n-gram matching is the draft-free alternative that derives proposals from prompt text.

[^parallel-draft]: Parallel Draft Models — `../raw/vllm/features/speculative_decoding/parallel_draft_model.md`, PARD proposal property, offline `LLM` and online `vllm serve` examples with `amd/PARD-Qwen3-0.6B`, `num_speculative_tokens: 12`, `method: draft_model`, and `parallel_drafting: true`, plus the `amd/pard` pre-trained weight collection.
