---
type: Concept
title: vLLM EAGLE Speculative Decoding
description: EAGLE and Eagle3 draft models proposing tokens for target verification via method eagle/eagle3, with independent draft tensor parallelism and pretrained speculator hubs.
tags: [vllm, speculative-decoding, eagle]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T13:00:00Z }
sources:
  - id: eagle
    resource: ../raw/vllm/features/speculative_decoding/eagle.md
    title: EAGLE Draft Models
---

vLLM runs EAGLE speculative decoding by pairing a target model with an EAGLE (Extrapolation Algorithm for Greater Language-model Efficiency) based draft model that generates proposals for target verification, selected through `speculative_config` with `method: eagle` or `method: eagle3`[^eagle].

## Configuration

EAGLE drafter (offline `LLM`)[^eagle]:

```python
llm = LLM(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    tensor_parallel_size=4,
    speculative_config={
        "model": "yuhuili/EAGLE-LLaMA3-Instruct-8B",
        "draft_tensor_parallel_size": 1,
        "num_speculative_tokens": 2,
        "method": "eagle",
    },
)
```

Eagle3 drafter (offline `LLM`)[^eagle]:

```python
llm = LLM(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    tensor_parallel_size=2,
    speculative_config={
        "model": "RedHatAI/Llama-3.1-8B-Instruct-speculator.eagle3",
        "draft_tensor_parallel_size": 2,
        "num_speculative_tokens": 2,
        "method": "eagle3",
    },
)
```

Target and draft tensor parallelism are set independently via `tensor_parallel_size` and `draft_tensor_parallel_size`; both examples propose `num_speculative_tokens: 2` per step[^eagle].

## Pre-trained draft models

EAGLE draft models are available on the Hugging Face Hub via the `RedHatAI/speculator-models` collection and `yuhuili` EAGLE model search[^eagle].

## Version note

On `vllm<0.7.0`, convert the speculative model with the linked conversion script and point `speculative_config.model` at the converted local path instead of the Hub ID[^eagle].

> Coverage limit: the source points to a detailed offline example including per-request acceptance-rate extraction in `examples/features/speculative_decoding/spec_decode_offline.py`; that example file was not present in `raw/` and was not inspected, so acceptance-rate extraction steps are not compiled here.

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — EAGLE/Eagle3 speculation is configured on the offline `LLM` class through `speculative_config`.
- Related to [vLLM Draft-Model Speculative Decoding](vllm-draft-model.md) — both configure a separate draft model through `speculative_config`, differing only in `method` (`eagle`/`eagle3` versus `draft_model`) and EAGLE-specific draft parallelism.
- Related to [vLLM Dynamic Speculative Decoding](vllm-dynamic-speculative-decoding.md) — Dynamic SD's batch-size-to-`K` table is tested with Eagle and Eagle-3 and can tune their draft-token count by concurrency.
- Related to [vLLM Per-Request Speculative Decoding Acceptance Metrics](vllm-per-request-spec-decode-metrics.md) — request-level acceptance metrics are the online-serving counterpart to the offline acceptance-rate extraction referenced for EAGLE.

[^eagle]: EAGLE Draft Models — `../raw/vllm/features/speculative_decoding/eagle.md`, EAGLE/Eagle3 offline `speculative_config` examples with independent `draft_tensor_parallel_size` and `num_speculative_tokens`, Hugging Face speculator hubs, `vllm<0.7.0` conversion-script guidance, and pointer to the offline acceptance-rate example.
