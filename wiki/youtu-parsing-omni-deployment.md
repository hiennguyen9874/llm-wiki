---
type: Software
title: Youtu-Parsing-Omni deployment
description: Youtu-Parsing-Omni deployment uses separate pinned vLLM and Transformers environments with task prompts, parsing-mode chat templates, and special-token-aware decoding.
tags: [ml, ocr, multimodal, deployment, vllm, transformers]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T14:47:26Z }
stale_after: 2027-02-02
sources:
  - id: youtu-omni-card
    resource: ../raw/Youtu-Parsing-Omni.md
    kind: model-card
    title: Youtu-Parsing-Omni model card
---

# Youtu-Parsing-Omni deployment

The model card reports two separate inference paths for [Youtu-Parsing-Omni](youtu-parsing-omni.md): a vLLM plugin server and direct Transformers inference, with incompatible pinned Transformers versions. The instructions below are **reported**, not tested; the referenced scripts and checkpoint code were not inspected.[^youtu-omni-card]

## Environments and server

Python ≥3.10 and CUDA GPUs are specified; audio and video also need `ffmpeg`. The serving setup pins `vllm==0.19.0` and `transformers==5.2.0`, installs the custom plugin without dependencies and removes `peft`; the separate Transformers setup pins `transformers==5.10.2`. The manual serving instructions explicitly override vLLM's `transformers<5` pin, so compatibility is a project-specific claim rather than an independently validated dependency solution.[^youtu-omni-card]

The card starts the server with `MODEL=tencent/Youtu-Parsing-Omni DATA_ROOT=/path/to/media GPU=0 bash scripts/vllm.sh`. It reports a foreground OpenAI-compatible endpoint on `127.0.0.1:8000/v1`, served name `Youtu-Parsing-Omni`, `PORT=8000` and GPU `0` by default. `DATA_ROOT` is the permitted directory for local media; the internal vLLM port defaults to `30000` via `VLLM_PORT`. Engine settings include 65,536 maximum model length and batched tokens, one sequence, GPU memory utilization 0.70, bfloat16, seed 1234, and per-prompt limits of 8 images, 4 videos and 8 audio inputs. The plugin reads additional `YOUTU_VITA_*` media token budgets, whose details are in an uninspected linked README.[^youtu-omni-card]

## Requests and decoding

- Select one of the eight task keys in the [model overview](youtu-parsing-omni.md); the corresponding prompts live in a linked JSON file not inspected here. In vLLM local media must be below `DATA_ROOT`.[^youtu-omni-card]
- Put media before text and set `chat_template_kwargs` to `{"enable_thinking": false, "enable_parsing": true}`. The example uses greedy decoding (`temperature=0`), `min_tokens=16`, `max_tokens=32768`, and `skip_special_tokens=false`, because special tokens encode coordinates. Obtain stop-token IDs for `<|image_pad|>` and `<|end_of_text|>` through the server's `/tokenize` endpoint rather than assuming fixed IDs.[^youtu-omni-card]
- Audio uses `audio_url`. For video the example sends a permitted local `video_url` and sets `mm_processor_kwargs` to `{"nframes": 64, "use_audio_in_video": true, "use_vision_in_video": true}`; the plugin is reported to decode both audio and frames.[^youtu-omni-card]
- Direct Transformers inference has no `DATA_ROOT` restriction in the example. It loads checkpoint code with `trust_remote_code=True`; the card recommends reviewing and pinning a Hugging Face commit via `--revision`. Treat this as code execution and review the actual checkpoint before use. Model Hub downloads and local checkpoint paths are supported as described, but no release availability was checked.[^youtu-omni-card]

## Evaluation and limits

The card's OmniDocBench recipe uses vLLM inference, one server per GPU, and an external official evaluator Docker image; it expects an `OMNIDOCBENCH` dataset directory with `images/` and `OmniDocBench.json`, and permits resuming by reusing the output directory. Predictions, results and logs are written under that output directory. These are instructions, not a reproduced benchmark.[^youtu-omni-card]

Only the supplied card was inspected; setup scripts, dependencies, plugin, prompts, checkpoint, license, Docker image and evaluator were not. No installation, server, inference or evaluation was run. Version, security and operational behavior therefore remain unverified.[^youtu-omni-card]

[^youtu-omni-card]: Tencent Youtu Lab, [Youtu-Parsing-Omni model card](../raw/Youtu-Parsing-Omni.md), §§ Quick Start › Installation, Serve with vLLM, Parse a file, Transformers, Output format; and OmniDocBench Evaluation; inspected 2026-11-02.
