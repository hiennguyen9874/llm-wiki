---
type: Concept
title: vLLM IO Processor Plugins
description: Pre- and post-processing plugins for pooling models that map custom inputs to model prompts and model outputs to custom outputs.
tags: [vllm, plugins, pooling]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: io-processor-plugins
    resource: ../raw/vllm/design/io_processor_plugins.md
    title: IO Processor Plugins
---

IO Processor plugins add custom pre- and post-processing around pooling-model inference[^io-processor-plugins]. A plugin accepts user-defined input, converts it into one or more model prompts for the model `encode` method, then converts `PoolingRequestOutput` objects into user-defined output — enabling flows such as image-in / image-out on pooling models[^io-processor-plugins].

vLLM performs no validation of the plugin-defined input or output data; the plugin is responsible for feeding the model correctly and returning correct data to the user[^io-processor-plugins].

## Scope and entry points

IO Processor plugins currently support only pooling models[^io-processor-plugins]. They are triggered via the `encode` method in `LLM` and `AsyncLLM`, or in online serving mode via the `/pooling` endpoint[^io-processor-plugins].

## IOProcessor interface

Plugins implement the generic `IOProcessor[IOProcessorInput, IOProcessorOutput]` abstract interface[^io-processor-plugins]:

- `__init__(vllm_config, renderer)`: receives engine config and renderer.
- `parse_data(data: object) -> IOProcessorInput`: validates user data and converts it into the input expected by `pre_process*`[^io-processor-plugins].
- `merge_sampling_params(params) -> SamplingParams`: merges input `SamplingParams` with the default; default returns the input or a fresh `SamplingParams`[^io-processor-plugins].
- `merge_pooling_params(params) -> PoolingParams`: merges input `PoolingParams` with the default; default returns the input or `PoolingParams(task="plugin")`[^io-processor-plugins].
- `pre_process(prompt, request_id, **kwargs) -> PromptType | Sequence[PromptType]` (abstract) and `pre_process_async(...)`: take validated plugin input and generate vLLM model prompts; the async default delegates to the sync method[^io-processor-plugins].
- `post_process(model_output: Sequence[PoolingRequestOutput], request_id, **kwargs) -> IOProcessorOutput` (abstract) and `post_process_async(model_output: AsyncGenerator[tuple[int, PoolingRequestOutput]], ...)`: take model outputs and generate custom plugin output[^io-processor-plugins].

The default `post_process_async` collects the async generator, sorts by index because outputs are not guaranteed to return in feed order, then delegates to sync `post_process`[^io-processor-plugins].

An external example generates geotiff images with the PrithviGeospatialMAE model via a segmentation plugin[^io-processor-plugins].

## Loading and precedence

Plugins load at engine startup, named by either[^io-processor-plugins]:

1. `EngineArgs`: `io_processor_plugin` on `AsyncLLM` / `LLM` offline, or `--io-processor-plugin` in serving mode.
2. Model HF config: `io_processor_plugin` field in the model `config.json`.

Setting the plugin via `EngineArgs` overrides the model HF config value[^io-processor-plugins].

## Coverage limits

- The external PrithviGeospatialMAE plugin implementation and the offline (`examples/pooling/plugin/prithvi_geospatial_mae_io_processor.py`) and online (`examples/pooling/plugin/prithvi_geospatial_mae_online.py`) examples were cited but not present in `raw/` and were not inspected[^io-processor-plugins].
- The `IOProcessor` interface source (`vllm.plugins.io_processors.interface.IOProcessor`) was compiled only from the excerpt in the design doc, not from inspected code[^io-processor-plugins].

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — offline `encode` in `LLM` / `AsyncLLM` and online `/pooling` are the trigger paths.

[^io-processor-plugins]: IO Processor Plugins — `../raw/vllm/design/io_processor_plugins.md`.
