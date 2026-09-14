---
type: Concept
title: vLLM MLP Speculative Decoding
description: MLP draft models conditioning proposals on context vectors and sampled tokens via method mlp_speculator, with independent draft tensor parallelism and IBM accelerator hubs.
tags: [vllm, speculative-decoding, mlp-speculator]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T14:00:00Z }
sources:
  - id: mlp
    resource: ../raw/vllm/features/speculative_decoding/mlp.md
    title: MLP Draft Models
---

vLLM runs MLP-speculator speculative decoding by pairing a target model with a draft model that conditions draft predictions on both context vectors and sampled tokens, selected through `speculative_config` with `method: mlp_speculator`[^mlp].

## Configuration

Offline (`LLM` class)[^mlp]:

```python
llm = LLM(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct",
    tensor_parallel_size=1,
    speculative_config={
        "model": "ibm-ai-platform/llama3-8b-accelerator",
        "draft_tensor_parallel_size": 1,
        "method": "mlp_speculator",
    },
)
```

Target and draft tensor parallelism are set independently via `tensor_parallel_size` and `draft_tensor_parallel_size`[^mlp]. The example generates with `SamplingParams(temperature=0.8, top_p=0.95)` through the unchanged offline `LLM.generate` path[^mlp].

## Pre-trained draft models

MLP-speculator draft models are available on the Hugging Face Hub[^mlp]:

- `ibm-ai-platform/llama-13b-accelerator`
- `ibm-ai-platform/llama3-8b-accelerator`
- `ibm-ai-platform/codellama-34b-accelerator`
- `ibm-ai-platform/llama2-70b-accelerator`
- `ibm-ai-platform/llama3-70b-accelerator`
- `ibm-granite/granite-3b-code-instruct-accelerator`
- `ibm-granite/granite-8b-code-instruct-accelerator`
- `ibm-granite/granite-7b-instruct-accelerator`
- `ibm-granite/granite-20b-code-instruct-accelerator`

## Known issue

`ibm-ai-platform/llama3-70b-accelerator` can fail with `AttributeError: 'MLPSpeculatorConfig' object has no attribute 'num_attention_heads'`; status is tracked in vLLM issues `#34106` and `#34163`[^mlp].

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — MLP speculation is configured on the offline `LLM` class through `speculative_config`.
- Related to [vLLM Draft-Model Speculative Decoding](vllm-draft-model.md) — both configure a separate draft model through `speculative_config`, differing in `method` (`mlp_speculator` versus `draft_model`) and MLP conditioning on context vectors plus sampled tokens.
- Related to [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — both configure a separate speculator with independent `draft_tensor_parallel_size`, differing in `method` (`mlp_speculator` versus `eagle`/`eagle3`) and pre-trained model hubs.

[^mlp]: MLP Draft Models — `../raw/vllm/features/speculative_decoding/mlp.md`, MLP conditioning on context vectors and sampled tokens, offline `mlp_speculator` example with independent `draft_tensor_parallel_size`, nine IBM accelerator Hub IDs, `llama3-70b-accelerator` `MLPSpeculatorConfig.num_attention_heads` failure with `#34106` / `#34163` tracking, and background pointers to the speculative-decoding guide and IBM technical report.
