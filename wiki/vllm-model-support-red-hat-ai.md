---
type: Concept
title: vLLM Model Support Check on Red Hat AI
description: Three-step compatibility check for vLLM on Red Hat AI via validated models, architecture lookup, and release-to-image version mapping.
tags: [vllm, red-hat, model-support]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T10:30:00Z }
sources:
  - id: redhat-vllm-support
    resource: ../raw/how-check-if-your-model-supported-vllm-red-hat-ai/index.md
    title: How to check if your model is supported by vLLM in Red Hat AI
---

Model support on Red Hat AI is determined by matching a model's architecture against the vLLM version shipped in a Red Hat release, after first checking whether Red Hat already validated the model end-to-end[^redhat-vllm-support].

## Validated-first check

- Check the Red Hat validated models program before inspecting config files manually[^redhat-vllm-support].
- Red Hat engineers test validated models with official Red Hat vLLM images to verify they run[^redhat-vllm-support].
- Browse the catalog on the RedHatAI Hugging Face page, or look for the **Model validated by Red Hat** badge on a specific model card[^redhat-vllm-support].
- The badge and model card specify which Red Hat OpenShift AI and Red Hat AI Inference versions were used for validation[^redhat-vllm-support].
- OpenShift AI users can also find validated models in the AI Hub **Models** section, with performance-insights data and ModelCar-image deployment[^redhat-vllm-support].
- Red Hat publishes a validated-models support matrix listing the minimum vLLM version alongside the corresponding Red Hat AI Inference and OpenShift AI releases[^redhat-vllm-support].

## Architecture fundamentals

- vLLM supports model architectures, not specific model names[^redhat-vllm-support].
- Read the `architectures` field in the model's `config.json`; for example, `Llama-3.3-70B-Instruct` and `Llama-3.1-8B-Instruct` both use `LlamaForCausalLM`[^redhat-vllm-support].
- If a model uses a supported architecture without unsupported customizations, it should run on a vLLM release supporting that architecture[^redhat-vllm-support].
- A newly released model reusing an existing architecture should run on any vLLM version that already supports that architecture[^redhat-vllm-support].

## Version-specific supported-models check

- Search the identified architecture on the upstream vLLM supported-models page[^redhat-vllm-support].
- That page defaults to the latest vLLM release; support is not necessarily backward compatible[^redhat-vllm-support].
- Use the docs version selector to check the specific vLLM version planned for deployment[^redhat-vllm-support].
- Example: `gemma-4-31b-it` uses `Gemma4ForConditionalGeneration`, supported by the latest vLLM at article time but not by v0.18.0 shipped in OpenShift AI and Red Hat AI Inference 3.4[^redhat-vllm-support].

## Red Hat image to vLLM version mapping

- Red Hat distributes vLLM as Red Hat AI Inference; the same images are available through OpenShift AI[^redhat-vllm-support].
- Find images in the `rhaii` namespace on the Red Hat Container Catalog, with per-accelerator images such as `rhaii/vllm-cuda-rhel9` for NVIDIA CUDA[^redhat-vllm-support].
- Determine the vLLM version in each Red Hat AI Inference release from its release notes[^redhat-vllm-support].
- Red Hat AI Inference ships about monthly as general availability (GA) or early access (EA); EA is unsupported and for testing newer models, while GA has a 7-month support window[^redhat-vllm-support].
- Between GA cycles, use preview images or EA releases for immediate access to newer architectures because upstream vLLM moves rapidly[^redhat-vllm-support].

## Day 0 path

- Use preview releases such as `rhaii-preview/vllm-cuda-rhel9` to test the latest vLLM releases and models, often with Day 0 support for new models[^redhat-vllm-support].

## Coverage limits

- The four `assets/` screenshots (validated-model collections, Llama 4 badge, supported-models matrix, docs version selector) were treated as illustrations; material claims above come from article prose and captions[^redhat-vllm-support].
- External destinations (validated-models catalog, support matrix, upstream supported-models page, container catalog, release notes) were not re-fetched; version examples are pinned to the 2026-08-12 article date[^redhat-vllm-support].

## Relationships

- Uses [vLLM Hugging Face Integration](vllm-huggingface-integration.md) — `config.json` `architectures` lookup maps to vLLM's architecture-to-class registry.

[^redhat-vllm-support]: How to check if your model is supported by vLLM in Red Hat AI — `../raw/how-check-if-your-model-supported-vllm-red-hat-ai/index.md`.
