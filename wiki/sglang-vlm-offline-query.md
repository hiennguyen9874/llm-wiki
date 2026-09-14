---
type: Concept
title: SGLang Offline VLM Query
description: Query VLMs via offline Engine API with raw images, processor output, or precomputed embeddings for Qwen2.5-VL and Llama 4.
tags: [sglang, vlm, multimodal, offline-inference]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: sgl-vlm-query
    resource: ../raw/sglang/advanced_features/vlm_query.mdx
    title: Query VLM with Offline Engine
---

SGLang's offline `Engine` API queries VLMs with three visual-input formats — raw images, HuggingFace processor output, or precomputed vision embeddings — demonstrated for Qwen2.5-VL and Llama 4; use one format per request and use embeddings to skip repeated vision-encoder work[^sgl-vlm-query].

## Three input formats

SGLang supports three ways to pass visual data, each optimized for different scenarios[^sgl-vlm-query]:

1. **Raw images** — pass PIL Images, file paths, URLs, or base64 strings directly; SGLang handles preprocessing automatically. Best for quick prototyping and simple applications.
2. **Processor output** — pre-process with a HuggingFace processor and pass the complete output dict with `format: "processor_output"`. Must use `input_ids` instead of a text prompt. Best for custom image transformations and existing pipelines.
3. **Precomputed embeddings** — pre-calculate visual embeddings with the vision encoder and pass them with `format: "precomputed_embedding"`. Best for repeated queries on the same images, caching, and high-throughput serving; source claims 30–50% speedup by avoiding redundant vision-encoder computation.

**Key rule**: within a single request, use only one format for all images; do not mix formats[^sgl-vlm-query].

## Common prompt construction

Both model examples build the prompt through `sglang.srt.parser.conversation.chat_templates`, copy the model chat template, append a user turn containing `conv.image_token`, append an empty assistant turn, set `conv.image_data = [image]`, and call `conv.get_prompt()`[^sgl-vlm-query]:

```python
conv = chat_templates[chat_template].copy()
conv.append_message(conv.roles[0], f"What's shown here: {conv.image_token}?")
conv.append_message(conv.roles[1], "")
conv.image_data = [image]
```

The tutorial image is the remote `examples/assets/example_image.png` loaded via PIL; that URL was not inspected beyond the source text[^sgl-vlm-query].

## Qwen2.5-VL

Example uses `model_path = "Qwen/Qwen2.5-VL-3B-Instruct"` with `chat_template = "qwen2-vl"`[^sgl-vlm-query].

Basic call:

```python
from sglang import Engine
llm = Engine(model_path=model_path, chat_template=chat_template, log_level="warning")
out = llm.generate(prompt=conv.get_prompt(), image_data=[image])
```

Processor-output call uses `AutoProcessor.from_pretrained(model_path, use_fast=True)` and passes `input_ids` plus the wrapped dict[^sgl-vlm-query]:

```python
processor_output = processor(images=[image], text=conv.get_prompt(), return_tensors="pt")
out = llm.generate(
    input_ids=processor_output["input_ids"][0].detach().cpu().tolist(),
    image_data=[dict(processor_output, format="processor_output")],
)
```

Precomputed-embedding call extracts the vision tower via `Qwen2_5_VLForConditionalGeneration.from_pretrained(model_path).eval().visual.cuda()`, runs it on `pixel_values` and `image_grid_thw`, and passes the result as `feature`[^sgl-vlm-query]:

```python
precomputed_embeddings = vision(
    processor_output["pixel_values"].cuda(), processor_output["image_grid_thw"].cuda()
)
multi_modal_item = dict(
    processor_output,
    format="precomputed_embedding",
    feature=precomputed_embeddings,
)
out = llm.generate(input_ids=input_ids, image_data=[multi_modal_item])
llm.shutdown()
```

## Llama 4 Scout

Example uses `model_path = "meta-llama/Llama-4-Scout-17B-16E-Instruct"` with `chat_template = "llama-4"`[^sgl-vlm-query].

Llama 4 requires more compute, so the source configures multi-GPU parallelism and large context[^sgl-vlm-query]:

```python
llm = Engine(
    model_path=model_path,
    enable_multimodal=True,
    attention_backend="fa3",
    tp_size=4,
    context_length=65536,
)
out = llm.generate(prompt=conv.get_prompt(), image_data=[image])
```

Processor-output form is the same `input_ids` + `format: "processor_output"` pattern as Qwen2.5-VL[^sgl-vlm-query].

Precomputed-embedding form runs the Llama 4 vision model plus multimodal projector explicitly[^sgl-vlm-query]:

```python
model = Llama4ForConditionalGeneration.from_pretrained(model_path, torch_dtype="auto").eval()
vision = model.vision_model.cuda()
multi_modal_projector = model.multi_modal_projector.cuda()
image_outputs = vision(
    processor_output["pixel_values"].to("cuda"),
    aspect_ratio_ids=processor_output["aspect_ratio_ids"].to("cuda"),
    aspect_ratio_mask=processor_output["aspect_ratio_mask"].to("cuda"),
    output_hidden_states=False,
)
vision_flat = image_outputs.last_hidden_state.view(-1, image_outputs.last_hidden_state.size(-1))
precomputed_embeddings = multi_modal_projector(vision_flat)
mm_item = dict(processor_output, format="precomputed_embedding", feature=precomputed_embeddings)
out = llm.generate(input_ids=input_ids, image_data=[mm_item])
```

## Relationships

- Uses [SGLang Data-Parallel Multimodal Encoder](sglang-dp-multimodal-encoder.md) — companion encoder-throughput optimization; offline precomputed embeddings skip repeated encoding per request while DP encoding parallelizes the encoder across batches.
- Uses [SGLang ViT CUDA Graphs for Multimodal Encoders](sglang-vit-cuda-graph.md) — alternative encoder-launch-overhead optimization for the same vision front end that precomputed embeddings bypass on cache hits.
- Uses [SGLang EPD Disaggregation](sglang-epd-disaggregation.md) — serving-side separation of encoder, prefill, and decode stages; offline embedding cache is the single-process analog for repeated-image efficiency.
- Uses [vLLM Multimodal Inputs](vllm-multimodal-inputs.md) — vLLM analog covering offline image, video, audio, embedding, and cached-UUID inputs versus SGLang's three offline visual formats.
- Uses [vLLM Prompt Embedding Inputs](vllm-prompt-embeds.md) — vLLM analog for passing precomputed embeddings directly instead of raw media.

## Coverage limits

- Source is a tutorial with inline Python examples, not an `Engine.generate` API reference; signatures, defaults, batching, multi-image, and video behavior beyond the single-image examples are not stated[^sgl-vlm-query].
- The 30–50% precomputed-embedding speedup is a source claim without benchmark setup and was not independently verified[^sgl-vlm-query].
- Remote example-image URL, `nest_asyncio` setup, GPU/CUDA prerequisites, and Llama 4 `fa3` / `tp_size=4` / 64K-context sizing were not validated by execution[^sgl-vlm-query].

[^sgl-vlm-query]: Query VLM with Offline Engine — `../raw/sglang/advanced_features/vlm_query.mdx`, covering offline Engine API, three visual-input formats with single-format-per-request rule, Qwen2.5-VL-3B-Instruct and Llama-4-Scout-17B-16E-Instruct prompt construction and basic / processor-output / precomputed-embedding calls, and Llama 4 `enable_multimodal`, `fa3`, `tp_size=4`, `context_length=65536` configuration.
