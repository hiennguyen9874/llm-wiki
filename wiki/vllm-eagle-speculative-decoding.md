---
type: Concept
title: vLLM EAGLE Speculative Decoding
description: EAGLE and Eagle3 draft models proposing tokens for target verification via method eagle/eagle3, with independent draft tensor parallelism and pretrained speculator hubs.
tags: [vllm, speculative-decoding, eagle]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-16T12:00:00Z }
sources:
  - id: eagle
    resource: ../raw/vllm/features/speculative_decoding/eagle.md
    title: EAGLE Draft Models
  - id: peagle
    resource: ../raw/speeding-llm-inference-p-eagle-vllm-speculators/index.md
    title: Speeding up LLM inference with P-EAGLE in vLLM Speculators
  - id: eagle3-fly
    resource: ../raw/fly-eagle3-fly-faster-inference-vllm-speculative-decoding/index.md
    title: 'Fly Eagle(3) fly: Faster inference with vLLM & speculative decoding'
---

vLLM runs EAGLE speculative decoding by pairing a target model with an EAGLE (Extrapolation Algorithm for Greater Language-model Efficiency) based draft model that generates proposals for target verification, selected through `speculative_config` with `method: eagle` or `method: eagle3`[^eagle].

Eagle 3 is a single-transformer-layer drafter that autoregressively generates multiple draft tokens from the target model's current state by reusing feature outputs from specific target layers concatenated with token embeddings; because it conditions on target features, an Eagle speculator only works for the model it was trained for[^eagle3-fly].

## Version and observability

vLLM introduced Eagle 1 and Eagle 3 in v0.8.5; v0.9.1 adds CUDA-graph support for Eagle 1/3 and speculative-decoding metrics including draft acceptance rate, per-position acceptance rates, and mean acceptance length (average tokens generated per verifier forward pass)[^eagle3-fly].

Eagle 3 online-serve example for Llama 3.3 70B (vLLM V1)[^eagle3-fly]:

```bash
VLLM_USE_V1=1 vllm serve meta-llama/Llama-3.3-70B-Instruct \
  --seed 42 \
  -tp 4 \
  --speculative-config '{"model": "yuhuili/EAGLE3-LLaMA3.3-Instruct-70B", "num_speculative_tokens": 3, "method": "eagle3", "draft_tensor_parallel_size": 1}'
```

The server API is unchanged; the source reports reduced end-to-end latency versus baseline in its text-generation example[^eagle3-fly].

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
- Related to [vLLM P-EAGLE Speculative Decoding](vllm-peagle-speculative-decoding.md) — P-EAGLE extends EAGLE-3 with single-pass K-token prediction depths via `PEagleDraftModel` inheriting from `Eagle3DraftModel`[^peagle].
- Related to [vLLM Speculative Decoding on AMD GPUs](vllm-speculative-decoding-amd-gpus.md) — EAGLE-3 target-layer fusion plus AMD throughput/acceptance evidence and LightSeek, Red Hat AI, and Inferact checkpoint names.
- Related to [Speculative Decoding Workload Fit and Tuning](speculative-decoding-practice-guide.md) — Eagle 3 request-rate, task-dependent, draft-length, and tree-decoding production evidence compiled from the same Red Hat source.

[^eagle]: EAGLE Draft Models — `../raw/vllm/features/speculative_decoding/eagle.md`, EAGLE/Eagle3 offline `speculative_config` examples with independent `draft_tensor_parallel_size` and `num_speculative_tokens`, Hugging Face speculator hubs, `vllm<0.7.0` conversion-script guidance, and pointer to the offline acceptance-rate example.

[^peagle]: Helen Zhao, Speeding up LLM inference with P-EAGLE in vLLM Speculators — `../raw/speeding-llm-inference-p-eagle-vllm-speculators/index.md` (Red Hat Developer, 2026-09-03), P-EAGLE as parallel EAGLE-3 extension with prediction depths and `PEagleDraftModel` inheritance.

[^eagle3-fly]: Alexandre Marques, Fly Eagle(3) fly: Faster inference with vLLM & speculative decoding — `../raw/fly-eagle3-fly-faster-inference-vllm-speculative-decoding/index.md` (Red Hat Developer, 2025-07-01), Eagle 3 single-layer target-feature mechanism and model-specificity, vLLM v0.8.5 introduction and v0.9.1 CUDA graphs plus acceptance metrics, Llama-3.3-70B `eagle3` serve example, and end-to-end latency example.
