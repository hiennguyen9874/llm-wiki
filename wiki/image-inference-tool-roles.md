---
type: Concept
title: Image Model, Library, and Workflow Roles
description: Distinguishes image-model weights from Diffusers Python pipelines, ComfyUI graph workflows, and the stable-diffusion.cpp C/C++ inference engine.
tags: [diffusers, comfyui, diffusion, inference, image-generation]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T05:14:15Z }
sources:
  - id: diffusion-model-explainer
    resource: ../raw/what-is-diffusion-model.md
    kind: article
    title: Vietnamese diffusion and image-model explainer
---

Image models such as Qwen-Image, SDXL, and FLUX supply learned weights; Diffusers, ComfyUI, and stable-diffusion.cpp are software for loading, composing, or executing generation pipelines, not themselves image models. The source's **reported** distinction is between a Python pipeline library, a graph-based UI with its own execution system, and a C/C++ inference engine.[^diffusion-model-explainer]

## Roles and interfaces

These are conceptual roles reported in sections 1–3 and 14–15, not a benchmark:[^diffusion-model-explainer]

| Tool | Role | Interface and typical use |
|---|---|---|
| Diffusers | Hugging Face modular Python library for diffusion and flow-based image, video, and audio pipelines | Python API for applications, research, customization, inference, training, and fine-tuning. |
| ComfyUI | Node-based UI plus workflow/inference execution system | Graphs joining model loading, conditioning, sampling, encoding/decoding, and output operations. |
| stable-diffusion.cpp | ggml-based C/C++ inference engine | C/C++, CLI, and API-oriented local inference and embedding; support depends on the model and backend. |

## Diffusers as pipeline composition

**Reported:** `DiffusionPipeline` can bundle a text encoder, UNet or image transformer, VAE, and scheduler. The source sketches loading these components, allocating memory, encoding a prompt, running iterative generation, decoding a latent, and returning an image. It presents LoRA, ControlNet, quantization, and CPU/GPU offload as customization areas (section 1).[^diffusion-model-explainer]

**Observed:** its illustrative call uses `DiffusionPipeline.from_pretrained("Qwen/Qwen-Image", dtype=torch.bfloat16, device_map="cuda")`. No package versions or tested environment are given. This is an inspected example, **not** a validated installation or API recipe.[^diffusion-model-explainer]

## ComfyUI as a visible workflow

**Reported:** ComfyUI exposes the pipeline as connected nodes. The explainer illustrates checkpoint loading, text encoding, sampling, VAE decoding, and saving; for editing it adds image loading and VAE encoding. It suggests composing reference images, masks, LoRA, ControlNet, upscaling, and other operations without writing the entire workflow in Python (section 2). These examples are not executable workflow exports or guarantees of universal model compatibility.[^diffusion-model-explainer]

## stable-diffusion.cpp as a separate engine

**Reported:** this C/C++ engine uses ggml, targets lightweight local inference across hardware, and supports architectures beyond the Stable Diffusion family. Quantization is presented as a means of reducing model-weight memory (section 3).[^diffusion-model-explainer]

For the maintained engine-specific capabilities and boundaries, see [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md), compiled from its project README rather than this overview.

## Architecture boundary and selection

- **Reported:** the source's stack diagram is explicitly conceptual. ComfyUI has its own execution/model-loading system and does **not** necessarily execute through Diffusers or stable-diffusion.cpp; custom nodes and backends vary (section 14).[^diffusion-model-explainer]
- **Synthesis:** choose a tool first by integration needs: Diffusers for a Python-defined pipeline, ComfyUI for a graph-defined workflow, or stable-diffusion.cpp for C/C++-oriented local inference. Then check the specific model, format, backend, and component support rather than treating these paths as interchangeable (sections 1–3 and 15).[^diffusion-model-explainer]
- **Reported opinion, unbenchmarked:** section 15's star ratings favor Diffusers for research, ComfyUI for complex visual workflows, and stable-diffusion.cpp for C/C++ embedding. They are qualitative preferences, not measured performance results.[^diffusion-model-explainer]

## Relationships

- Executes or composes the components explained in [Latent Image Generation Pipeline](latent-image-generation.md).
- [ComfyUI-GGUF Quantized Model Support](comfyui-gguf.md) documents a specific custom-node integration, distinct from both the ComfyUI host and the separate stable-diffusion.cpp engine.
- [Qwen-Image-2.1 Text-to-Image and Editing Model](qwen-image-2-1.md) records a model-specific Diffusers recipe; this explainer's `Qwen/Qwen-Image` example is not that recipe.

## Coverage and trust limits

- **Observed:** the complete single-file Vietnamese explainer, including code, inline diagrams, and the table, was statically inspected. No local material attachments or includes are referenced.
- Author, publisher, publication/capture date, immutable revision, license, and canonical explainer URL are not supplied. Linked Diffusers documentation, ComfyUI documentation, GitHub README, and model repositories were not fetched or independently checked in this ingest.
- No code, installation, workflow, quantization, memory measurement, backend, or comparative benchmark was executed. All software behavior here is **reported** or explicitly labeled **synthesis**.
- The imaginary “40+ GB” Qwen weight example, star scores, and broad research-update-speed comparisons are excluded as sizing or performance evidence. Component versions, exact compatibility matrices, and runnable workflow definitions are not established by this source.

[^diffusion-model-explainer]: [Vietnamese explainer](../raw/what-is-diffusion-model.md), opening model/tool distinction; sections 1 “Diffusers là gì?”, 2 “ComfyUI là gì?”, 3 “stable-diffusion.cpp là gì?”, 14 on stack placement and the explicit conceptual-diagram caveat, and 15 “Một bảng so sánh thực tế”. Upstream links are citations within the explainer, not independently inspected sources in this operation.
