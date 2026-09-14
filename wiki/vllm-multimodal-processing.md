---
type: Concept
title: vLLM Multimodal Data Processing
description: Placeholder-to-input correspondence via HF-processor replay, dummy text, prompt updates, output caching, and GPU-fused normalization.
tags: [vllm, multimodal, preprocessing]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: mm-processing
    resource: ../raw/vllm/design/mm_processing.md
    title: Multi-Modal Data Processing
---

vLLM recreates Hugging Face processor multimodal outputs without the original text to map placeholder feature tokens such as `<image>` to multimodal inputs such as raw images, enabling chunked prefill and prefix caching, with processor-output caching and GPU-fused normalization as performance optimizations[^mm-processing].

## Processor role

- `BaseMultiModalProcessor` provides the correspondence between placeholder feature tokens and multimodal inputs based on HF processor outputs[^mm-processing].
- This correspondence supports optimizations such as chunked prefill and prefix caching[^mm-processing].
- In vLLM's rendering pipeline, tokenization runs as a separate step before multimodal processing, so `BaseMultiModalProcessor` must recreate the output of calling the HF processor end-to-end without seeing the original text[^mm-processing].
- The replay is achieved through dummy input text and prompt update detection[^mm-processing].

## Dummy input text

- Since Transformers 5.10, `ProcessorMixin` allows multimodal inputs to be passed by themselves, but some subclasses such as `ChameleonProcessor` and older out-of-tree implementations may still define their own `__call__` assuming text with placeholder tokens is present[^mm-processing].
- Because vLLM no longer has the original text at this stage, each model defines how to generate dummy text from the number of multimodal inputs via `get_dummy_text`[^mm-processing].
- The model override of `_get_hf_processor_text` returns that dummy text so `_apply_hf_processor_main` can pass it with the multimodal inputs to the HF processor and obtain processed multimodal data[^mm-processing].
- Input adaptation is isolated in `_preprocess_hf_mm_data`, for example renaming keys such as `audios` to `audio` or injecting extra arguments such as `sampling_rate`, without reimplementing the whole main method[^mm-processing].
- Output adaptation is isolated in `_postprocess_hf_mm_data` for the same reason[^mm-processing].

## Prompt update detection

- HF processors update the prompt with placeholder tokens, for example inserting feature placeholder tokens such as `<image><image>...<image>` at the start of the string, with count equal to feature size, or replacing existing input placeholders such as `<image>` with the expanded feature-placeholder sequence[^mm-processing].
- Knowing which tokens were updated is key to mapping placeholder feature tokens back to multimodal inputs[^mm-processing].
- Because the HF processor is called without input text, vLLM performs this update itself by representing the needed changes as `PromptUpdate` in `_get_prompt_updates` and applying them via `_apply_prompt_updates`[^mm-processing].
- Some HF processors also transform the prompt independently of multimodal inputs, such as `ChameleonProcessor` appending a separator token for chat mode[^mm-processing].
- Since prompt tokens also bypass the HF processor, such transformations are replicated via `_postprocess_prompt` before prompt updates are located or applied[^mm-processing].

## Processor output caching

- Some HF processors, such as the Qwen2-VL processor, are very slow, so vLLM caches multimodal HF-processor outputs to avoid reprocessing the same image or other input[^mm-processing].
- On new data, vLLM separates cached from missing items, passes the missing items to the HF processor in one batch, caches the results, then merges cached and newly processed items[^mm-processing].

## GPU-fused normalization

- To accelerate decoding, resizing, normalization, and rescaling, vLLM offloads heavy numerical preprocessing from CPU to GPU and optimizes data movement[^mm-processing].
- Traditionally the CPU divided pixels by 255, subtracted mean, and divided by standard deviation; the fused path combines rescaling and normalization into one GPU-side affine transform `y = x * weight + bias`[^mm-processing].
- A dedicated `FusedInputNorm` module bakes the `1/255` rescale factor into `weight` and `bias`: `weight` encodes standard deviation plus rescale, while `bias` encodes mean plus rescale, so raw `0–255` pixels are normalized without an explicit separate divide-by-255 step[^mm-processing].

### Optimized uint8 data path

- Fused normalization keeps the transfer path from entrypoint through engine core to GPU memory in `uint8`, halving PCIe bandwidth and reducing CPU memory footprint[^mm-processing].
- Only after reaching GPU memory is data cast to `fp32` for `FusedInputNorm` for numerical accuracy, then to `bf16` for later layers, all on GPU without host-side conversions[^mm-processing].
- Overall path: entrypoint `uint8` to engine core `uint8` to GPU memory `uint8`, then GPU-local `fp32` `FusedInputNorm` to `bf16` output[^mm-processing].

### Toggle and model support

- The GPU-side path is controlled by `mm_device_do_normalize`: `True` uses GPU `FusedInputNorm`, `False` falls back to the old CPU path[^mm-processing].
- The flag is enabled by default for all models that support it[^mm-processing].
- Currently enabled by default for[^mm-processing]:

| name | Architecture | Example HF models |
|------|--------------|-------------------|
| `qwen2-vl` | `Qwen2VLForConditionalGeneration` | `Qwen/Qwen2-VL-2B-Instruct`, etc. |
| `qwen2.5-vl` | `Qwen2_5_VLForConditionalGeneration` | `Qwen/Qwen2.5-VL-3B-Instruct`, etc. |

### Gains

- CPU arithmetic for normalization and rescaling is removed[^mm-processing].
- Sending `uint8` instead of `bf16` cuts transfer volume by 50%[^mm-processing].
- The fused kernel is lightweight and can often merge with subsequent CUDA operations, adding little GPU cost[^mm-processing].

## Relationships

- Uses [vLLM Hugging Face Integration](vllm-huggingface-integration.md) — replays HF processor behavior and tokenizer-adjacent prompt handling without the original text.
- Enables [vLLM Prefix Caching](vllm-prefix-caching.md) — placeholder-to-input correspondence is part of what makes prefix reuse possible for multimodal prompts; the prefix-caching concept covers the complementary image-hash `extra hash` mechanism.

## Coverage limits

- Cross-references to `../configuration/optimization.md` for chunked prefill and `../features/automatic_prefix_caching.md` were not present under `raw/` and were not inspected; maintained prefix-caching synthesis is in [vLLM Prefix Caching](vllm-prefix-caching.md)[^mm-processing].
- The Qwen2-VL slowness issue link, `BaseMultiModalProcessor` and renderer code symbols, and `FusedInputNorm` implementation details were not verified against a live checkout[^mm-processing].

[^mm-processing]: Multi-Modal Data Processing — `../raw/vllm/design/mm_processing.md`, covering `BaseMultiModalProcessor` correspondence, tokenization-before-processing pipeline, dummy text and HF input/output adaptation, `PromptUpdate` detection and `_postprocess_prompt`, processor output caching, and GPU-fused `FusedInputNorm` with `uint8` path, `mm_device_do_normalize`, Qwen2-VL/Qwen2.5-VL defaults, and performance gains.
