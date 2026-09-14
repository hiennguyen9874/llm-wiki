---
type: Concept
title: vLLM Memory Conservation
description: Reducing vLLM GPU and CPU memory with tensor parallelism, quantization, context and batch caps, CUDA-graph tuning, cache sizes, and multimodal limits.
tags: [vllm, memory, deployment, configuration]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: conserve-memory
    resource: ../raw/vllm/configuration/conserving_memory.md
    title: Conserving Memory
---

vLLM conserves memory by sharding weights across GPUs, loading lower-precision checkpoints, capping context length and batch size, shrinking or disabling CUDA-graph capture, bounding CPU and multimodal caches, and limiting multimodal items and processor output size[^conserve-memory].

## Tensor parallelism

Set `tensor_parallel_size` to split the model across GPUs[^conserve-memory]:

```python
from vllm import LLM

llm = LLM(model="ibm-granite/granite-3.1-8b-instruct", tensor_parallel_size=2)
```

- Do not call CUDA-device functions such as `torch.accelerator.set_device_index` before initializing vLLM; it can cause errors like `RuntimeError: Cannot re-initialize CUDA in forked subprocess`. Select devices with `CUDA_VISIBLE_DEVICES` instead[^conserve-memory].
- With tensor parallelism enabled, each worker reads the whole checkpoint before sharding, so disk-read time grows with the parallel size. The source points to `examples/features/sharded_state/load_sharded_state_offline.py` for converting to a sharded checkpoint that keeps load time roughly constant; that script was absent from `raw/` and was not inspected[^conserve-memory].

## Quantization

Quantized checkpoints use less memory at lower precision[^conserve-memory]:

- Static quantization: download a pre-quantized model from Hugging Face Hub, including popular collections under RedHatAI, and use it directly without extra configuration[^conserve-memory].
- Dynamic quantization: pass the `quantization` option; the source defers detail to the quantization feature documentation[^conserve-memory].

## Context length and batch size

Limit `max_model_len` and `max_num_seqs` to reduce KV-cache and activation memory[^conserve-memory]:

```python
from vllm import LLM

llm = LLM(model="Qwen/Qwen2.5-VL-3B-Instruct", max_model_len=2048, max_num_seqs=2)
```

## CUDA-graph memory

CUDA graphs speed up inference but consume extra GPU memory. Tune `compilation_config` to balance speed against memory, for example by restricting capture sizes[^conserve-memory]:

```python
from vllm import LLM
from vllm.config import CompilationConfig, CompilationMode

llm = LLM(
    model="meta-llama/Llama-3.1-8B-Instruct",
    compilation_config=CompilationConfig(
        mode=CompilationMode.VLLM_COMPILE,
        # By default, it goes up to max_num_seqs
        cudagraph_capture_sizes=[1, 2, 4, 8, 16],
    ),
)
```

Disable graph capture entirely with `enforce_eager` when memory matters more than graph speedup[^conserve-memory]:

```python
from vllm import LLM

llm = LLM(model="meta-llama/Llama-3.1-8B-Instruct", enforce_eager=True)
```

## CPU RAM cache sizes

If CPU RAM is exhausted[^conserve-memory]:

- Multimodal models only: set `mm_processor_cache_gb` for the multimodal processor cache; default is 4 GiB.
- CPU backend only: set `VLLM_CPU_KVCACHE_SPACE` for KV-cache space; default is 4 GiB.

## Multimodal per-prompt limits

Use `limit_mm_per_prompt` to accept fewer multimodal items per prompt and lower the model memory footprint[^conserve-memory]:

```python
from vllm import LLM

# Accept up to 3 images and 1 video per prompt
llm = LLM(
    model="Qwen/Qwen2.5-VL-3B-Instruct",
    limit_mm_per_prompt={"image": 3, "video": 1},
)
```

Disable an unused modality by setting its limit to zero, for example image-only service with no video allocation[^conserve-memory]:

```python
from vllm import LLM

# Accept any number of images but no videos
llm = LLM(
    model="Qwen/Qwen2.5-VL-3B-Instruct",
    limit_mm_per_prompt={"video": 0},
)
```

Run a multimodal model text-only by disabling its modalities[^conserve-memory]:

```python
from vllm import LLM

# Don't accept images. Just text.
llm = LLM(
    model="google/gemma-3-27b-it",
    limit_mm_per_prompt={"image": 0},
)
```

### Configurable size hints

`limit_mm_per_prompt` also accepts a configurable form with `count` plus optional profiling size hints[^conserve-memory]:

- `image`: `{"count": int, "width": int, "height": int}`
- `video`: `{"count": int, "num_frames": int, "width": int, "height": int}`
- `audio`: `{"count": int, "length": int}`

Example[^conserve-memory]:

```python
from vllm import LLM

# Up to 5 images per prompt, profile with 512x512.
# Up to 1 video per prompt, profile with 32 frames at 640x640.
llm = LLM(
    model="Qwen/Qwen2.5-VL-3B-Instruct",
    limit_mm_per_prompt={
        "image": {"count": 5, "width": 512, "height": 512},
        "video": {"count": 1, "num_frames": 32, "width": 640, "height": 640},
    },
)
```

Behavior notes[^conserve-memory]:

- An integer remains valid for backward compatibility and means `{"count": <int>}`; integer and configurable forms may be mixed, e.g. `{"image": 5, "video": {"count": 1, "num_frames": 32, "width": 640, "height": 640}}`.
- Size hints affect activation-memory profiling only by shaping the dummy inputs used to reserve activation sizes; they do not change inference-time input processing.
- Hints larger than the model maximum are clamped to the effective maximum, possibly with a logged warning.
- These hints do not limit encoder-cache size, which is determined by actual runtime inputs.

Detailed option types are named as `ImageDummyOptions`, `VideoDummyOptions`, and `AudioDummyOptions` under `vllm.config.multimodal`; those symbols were not inspected beyond this source[^conserve-memory].

## Multimodal processor arguments

For some models, `mm_processor_kwargs` shrinks processed multimodal inputs and saves memory[^conserve-memory]:

```python
from vllm import LLM

# Available for Qwen2-VL series models
llm = LLM(
    model="Qwen/Qwen2.5-VL-3B-Instruct",
    mm_processor_kwargs={"max_pixels": 768 * 768},  # Default is 1280 * 28 * 28
)

# Available for InternVL series models
llm = LLM(
    model="OpenGVLab/InternVL2-2B",
    mm_processor_kwargs={"max_dynamic_patch": 4},  # Default is 12
)
```

## Relationships

- Uses [vLLM Tensor and Pipeline Parallel Scaling](vllm-parallelism-scaling.md) — single-node `tensor_parallel_size` weight sharding as one memory-conservation strategy.
- Uses [vLLM Quantization Methods and Toolchains](vllm-quantization-methods.md) — static pre-quantized checkpoints versus load-time `quantization` selection.
- Uses [vLLM CUDA Graphs Modes and Dispatch](vllm-cuda-graphs.md) — `cudagraph_mode`, capture sizes, and eager fallback behind the `compilation_config` and `enforce_eager` memory trade-off.
- Uses [vLLM Multimodal Inputs](vllm-multimodal-inputs.md) — `limit_mm_per_prompt` gating shared with the general multimodal input path.
- Uses [vLLM Multimodal Data Processing](vllm-multimodal-processing.md) — processor cache and `mm_processor_kwargs` sizing for multimodal preprocessing.
- Uses [vLLM Entrypoints](vllm-entrypoints.md) — offline `LLM` options through which all of these memory settings are supplied.

## Coverage limits

- `examples/features/sharded_state/load_sharded_state_offline.py`, `vllm.config.multimodal` dummy-option symbols, `torch.accelerator.set_device_index`, and external RedHatAI Hugging Face collections were not inspected beyond this source's summary[^conserve-memory].
- Quantization-format detail is deferred to the quantization feature documentation rather than repeated here.

[^conserve-memory]: Conserving Memory — `../raw/vllm/configuration/conserving_memory.md`, covering tensor parallelism and CUDA initialization, static versus dynamic quantization, `max_model_len`/`max_num_seqs`, `compilation_config.cudagraph_capture_sizes` and `enforce_eager`, `mm_processor_cache_gb` and `VLLM_CPU_KVCACHE_SPACE`, integer/zero/configurable `limit_mm_per_prompt` with profiling-only size hints, and model-specific `mm_processor_kwargs`.
