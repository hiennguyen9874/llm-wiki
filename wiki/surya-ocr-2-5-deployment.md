---
type: Concept
title: Surya OCR 2.5 deployment
description: Surya OCR 2.5 deployment uses a shared inference server for page OCR, layout, and tables, with backend-specific lifecycle, decoding, and compatibility constraints.
tags: [ml, ocr, deployment, inference, document-parsing]
status: draft
created: 2026-10-30
stale_after: 2027-04-30
generated: { by: llm-wiki-agent/1, at: 2026-10-30T02:11:12Z }
sources:
  - id: surya-25-card
    resource: ../raw/surya-ocr-2.5-hf.md
    kind: model-card
    title: Surya OCR 2.5 model card
---

# Surya OCR 2.5 deployment

**Reported:** [Surya OCR 2.5](surya-ocr-2-5.md) uses `SuryaInferenceManager` to share one VLM server among recognition, layout and table predictors; the separate Torch line detector does not need that server. The documented default is vLLM on NVIDIA or llama.cpp elsewhere, automatically spawned unless `SURYA_INFERENCE_URL` points to an existing OpenAI-compatible endpoint.[^surya-25-card]

## Setup and lifecycle

Install with `pip install surya-ocr`. The documented NVIDIA setup needs Docker and NVIDIA Container Toolkit; CPU/Apple Silicon needs `llama-server`. `surya_ocr`, `surya_layout`, `surya_table` and `surya_detect` accept an image, PDF or directory; their results are written as JSON. Commands ordinarily shut down the spawned server at exit; `--keep_server` or `SURYA_INFERENCE_KEEP_ALIVE=1` retains it, requiring a later container stop or process termination. Reusing a server avoids repeated startup and model loading.[^surya-25-card]

The Python interface constructs `RecognitionPredictor(manager)` and invokes it on images; the default is one VLM call per page. Passing `LayoutPredictor` results selects per-block OCR. Migrating from v1 replaces `FoundationPredictor` with the shared manager and changes output schemas, notably `text_lines` to HTML-bearing `blocks`.[^surya-25-card]

## Serving and decoding constraints

- Set `SURYA_INFERENCE_PARALLEL` for client concurrency; the card lists default 8 and recommends matching llama-server `--parallel`. vLLM sequence and batched-token limits, resolution and MTP also affect throughput. MTP automatically activates only when the checkpoint declares a head; `VLLM_ENABLE_MTP` overrides it.[^surya-25-card]
- The documented experimental Apple Silicon MLX backend is opt-in via `SURYA_INFERENCE_BACKEND=mlx` and `SURYA_MLX_MODEL`; the card reports testing `mlx-vlm==0.7.10`. Its server ignores request stop strings, so a checkpoint must emit an end token rather than rely on `SURYA_STOP_STRINGS`.[^surya-25-card]
- Self-hosted output must retain special tokens (`llama-server --special`); use the package's `clean_block_html` / `parse_full_page_html` to decode compact parent/ghost table spans. The lower-level `compact.decode` alone does not complete that conversion.[^surya-25-card]
- The source warns that the stated `surya-ocr` OpenCV pin conflicts with vLLM 0.25's requirement in one Python environment and recommends separate environments; the default GPU backend runs vLLM in Docker. These version-specific claims may change.[^surya-25-card]
- Full table mode outputs HTML, including spanning cells; simple row/column geometry is supported by Surya 2 checkpoints, not 2.5. Layout results include ordered boxes, labels, token-budget estimate, confidence, raw output and an error flag.[^surya-25-card]

**Evidence limit:** This is a static reading of the vendor card, not an implementation audit. Referenced package code, settings, backend binaries, model weights, license and external documentation were not inspected; no install, network call, server, inference or test was run. Exact version and revision of the capture are unavailable, so verify current APIs and security/privacy settings before deployment.[^surya-25-card]

## Relationships

- **Deploys:** [Surya OCR 2.5](surya-ocr-2-5.md), including its full-page and layout-first paths.[^surya-25-card]

[^surya-25-card]: Datalab, local [Surya 2.5 model card](../raw/surya-ocr-2.5-hf.md), §§ Installation, Upgrading from Surya v1, Usage, Server lifecycle, OCR, Layout and reading order, Table Recognition, Output format, Inference Backends, MLX backend and Limitations (inspected 2026-10-30).
