---
type: Concept
title: Nemotron 3.5 Parse deployment
description: Nemotron 3.5 Parse deployment uses a Transformers remote-code path or a vLLM plugin with one-token speculative decoding and structured postprocessing.
tags: [ml, ocr, inference, deployment, document-parsing]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T14:47:22Z }
stale_after: 2027-05-02
sources:
  - id: nemotron-35-card
    resource: ../raw/Nemotron-3.5-Parse.md
    kind: model-card
    title: Nemotron 3.5 Parse model card
---

# Nemotron 3.5 Parse deployment

**Reported:** [Nemotron 3.5 Parse](nemotron-parse-3-5.md) supports a Transformers inference path and a separate vLLM plugin path. The model card's reference system is Linux with NVIDIA H100 and BF16; compatibility and performance were not tested here.[^nemotron-35-card]

## Transformers

The example uses Python 3.12, `transformers==5.14.1`, `torchvision==0.26.0` and `timm==1.0.22`, with `AutoModel` and `AutoProcessor` loaded from `nvidia/Nemotron-3.5-Parse` using `trust_remote_code=True`. The documented CUDA BF16 example converts the image to RGB, disables automatic special tokens, uses the model's control-token task prompt, and sets `max_new_tokens=8744`. Loading remote code executes downloaded code, so review and pin the model revision and dependencies before use; no revision was pinned in the card.[^nemotron-35-card]

## vLLM and postprocessing

The card specifies Python 3.12 and plugin-compatible `vllm>=0.25.0,<0.33`, installed from a downloaded model repository with `.[vllm,client]`. It says one-token MTP and the compatible FA3 scheduler are enabled automatically. The offline example includes an image placeholder `<pad>` before the task prompt and disables automatic special tokens; the server example supplies image and text separately via an OpenAI-compatible endpoint and uses a repository chat template. The stated examples use BF16, FA3, one image per prompt and disabled prefix caching.[^nemotron-35-card]

For standalone postprocessing, the card downloads `postprocessing.py`, `latex2html.py` and `nemotron_parse/**`, adds `beautifulsoup4==4.13.3`, and calls `postprocess_document(generated_text, image_size=image.size)` to obtain Markdown and normalized/pixel-box blocks. Table formats include LaTeX, HTML, Markdown, JSON, hierarchical JSON and CSV; flat formats flatten spans. Header inference, numeric splitting and chart-caption association have controls; defaults can affect downstream interpretation.[^nemotron-35-card]

## Evidence limits

These are vendor-documented, version-sensitive instructions, not a reproduced installation. The repository code, plugin, chat template, serving and postprocessing guides, dependencies and weights were not present with the local card or independently inspected; external downloads and inference were not run. See [evaluation](nemotron-parse-3-5-evaluation.md) for measured-pass caveats.[^nemotron-35-card]

[^nemotron-35-card]: NVIDIA, [Nemotron 3.5 Parse model card](../raw/Nemotron-3.5-Parse.md), §§ Quick Start, Postprocessing, Inference with vLLM, and Software Integration.
