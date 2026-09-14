---
type: Concept
title: vLLM torch.compile for Multimodal Encoders
description: Compiling multimodal encoders with support_torch_compile gating, encoder compile ranges, and vision troubleshooting.
tags: [vllm, torch-compile, multimodal, encoder]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T08:51:11Z }
sources:
  - id: torch-compile-mm
    resource: ../raw/vllm/design/torch_compile_multimodal.md
    title: torch.compile with Multimodal Encoders
---

`@support_torch_compile` now works for multiple nn-module components in one model, so multimodal encoders such as LLaMA 4 and Qwen-VL vision blocks can be compiled independently of the text backbone when `compile_mm_encoder` is enabled[^torch-compile-mm].

## Enablement

- Off by default; enable with `compile_mm_encoder: true` in the compilation config on models that carry the decorator[^torch-compile-mm].
- Gate encoder compilation with `enable_if=should_torch_compile_mm_encoder` in `@support_torch_compile`[^torch-compile-mm].
- Mark encoder components with `is_encoder=True`, which signals that compile ranges cannot be inferred and selects the encoder range policy[^torch-compile-mm].
- The decorator uses the class name as the cache-directory prefix, avoiding collisions between independently compiled sub-modules such as the vision encoder and the text backbone[^torch-compile-mm].

```python
@support_torch_compile(
    enable_if=should_torch_compile_mm_encoder,
    is_encoder=True,
)
class VisionEncoder(...):
    ...
```

## Configuration inheritance

- Except for `compile_mm_encoder: true`, the multimodal encoder inherits the same compilation config as the text LLM[^torch-compile-mm].
- The source notes this may be extended with encoder-specific configuration in the future[^torch-compile-mm].

## Bring-up for a new module

- Follow the same incremental workflow as the text backbone: start with small modules such as basic MLP layers, then widen scope until performance and compile-time trade off acceptably[^torch-compile-mm].
- Use `tlparse` to identify and eliminate recompiles and graph breaks[^torch-compile-mm].
- Use `dynamic_arg_dims` and a proper `dynamic_shapes_config` to handle dynamism[^torch-compile-mm].
- Reported example: compiling the vision block of `Qwen2_5_vl` gave about 4.5% end-to-end improvement with some increase in compilation time[^torch-compile-mm].

## Compile ranges

- The backend normally uses `max_batch_size` to infer compilation ranges for dynamic shapes, but encoder input shapes have an unspecified range that is difficult to infer[^torch-compile-mm].
- `is_encoder=True` tells `torch.compile` the range cannot be inferred; the default encoder range is `(1, MAX_INT)`[^torch-compile-mm].
- The source notes this range may be tightened later for better performance[^torch-compile-mm].

## CUDAGraphs limit

- Compilation for multimodal encoders with CUDAGraph integration has not yet been explored; behavior is currently unspecified[^torch-compile-mm].
- This is distinct from budget-based encoder CUDA-graph capture, which is compiled separately in [vLLM Encoder CUDA Graphs for Vision Transformers](vllm-encoder-cuda-graphs.md).

## Troubleshooting

### Graph breaks in vision encoders

- Identify breaks with `TORCH_LOGS="+dynamo" vllm serve <MODEL>`[^torch-compile-mm].
- Common causes[^torch-compile-mm]:
  - **Dynamic image sizes**: handle variable resolutions with `dynamic_shapes_config`.
  - **Untraceable operations**: some ops such as `to_list` may not be supported by Dynamo.
  - **Conditional processing**: data-dependent branching on image properties.

### Compilation errors

1. Verify the model works without compilation[^torch-compile-mm]:

```bash
vllm serve <model> --compilation-config='{"mode":0,"compile_mm_encoder":"false"}'
```

2. Re-enable the encoder path with debug logging[^torch-compile-mm]:

```bash
VLLM_LOGGING_LEVEL=DEBUG vllm serve <model> --compilation-config='{"compile_mm_encoder":"true"}'
```

3. Report bugs through GitHub issues[^torch-compile-mm].

## Coverage limits

- Linked `torch_compile.md` and `debug_vllm_compile.md` were not re-inspected here; their maintained synthesis lives in [vLLM torch.compile Integration](vllm-torch-compile.md) and [Debugging vLLM-torch.compile Integration](vllm-debug-torch-compile.md)[^torch-compile-mm].
- `../features/multimodal_inputs.md` and `../features/disagg_encoder.md` exist under `raw/` but were not inspected because they are peripheral See Also links[^torch-compile-mm].
- `../models/supported_models.md` is referenced by the source but absent from `raw/` and was not inspected[^torch-compile-mm].
- External PR 23207, the `tlparse` repository, and GitHub issue links were not inspected[^torch-compile-mm].
- The source `Common pitfalls` heading has no content and contributes no claims[^torch-compile-mm].

## Relationships

- Uses [vLLM torch.compile Integration](vllm-torch-compile.md) — encoder compilation reuses the text-backbone mechanism plus `compile_mm_encoder` gating, `is_encoder` ranges, and per-class cache prefixes.
- Depends on [Debugging vLLM-torch.compile Integration](vllm-debug-torch-compile.md) — incremental bring-up, `tlparse` recompile/graph-break analysis, and `dynamic_shapes_config` handling are the same workflow.
- Uses [vLLM Encoder CUDA Graphs for Vision Transformers](vllm-encoder-cuda-graphs.md) — separate budget-based encoder-graph optimization; its interaction with encoder `torch.compile` is currently unspecified.

[^torch-compile-mm]: torch.compile with Multimodal Encoders — `../raw/vllm/design/torch_compile_multimodal.md`, covering `@support_torch_compile` enablement with `enable_if` and `is_encoder`, `compile_mm_encoder` config inheritance, incremental bring-up, `(1, MAX_INT)` encoder ranges, unspecified CUDAGraph behavior, and vision troubleshooting.
