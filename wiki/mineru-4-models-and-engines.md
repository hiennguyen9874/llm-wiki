---
type: Concept
title: MinerU 4 models and inference engines
description: MinerU 4 independently selects small-model ONNX or Torch execution and a local or remote VLM engine, with distinct model assets and device policies.
tags: [ml, ocr, inference, deployment]
status: draft
created: 2026-10-29
generated: { by: llm-wiki-agent/1, at: 2026-10-29T13:55:01+07:00 }
stale_after: 2027-04-29
sources:
  - id: mineru-repo
    resource: ../raw/MinerU/README.md
    scope: ../raw/MinerU/
    kind: code
    revision: b7f3dd0c5f6e6d66a298239ffd02b328b873918e
    title: MinerU repository 4.0.12
---

# MinerU 4 models and inference engines

**Observed:** MinerU 4 separates the small-model backend from VLM engine selection. The former runs layout, OCR, formula and table components; standard/advanced PDF processing additionally uses a VLM. The model registry selects separate asset bundles for ONNX, Torch and the VLM engine.[^mineru-repo]

## Model components

| Component | Assets or role in this snapshot |
| --- | --- |
| Layout | PP-DocLayoutV2 layout model. |
| Text OCR | PP-OCRv6 Tiny detector and Small recognizer. |
| Seal OCR | PP-OCRv4 detector with shared recognizer. |
| Formula | PP-FormulaNet plus-M. |
| Tables | SLANet Plus, UNet and table classifier; these table assets are ONNX even in the Torch bundle. |
| VLM | MinerU2.5-Pro-2605-1.2B; llama.cpp selects Q8 GGUF plus a multimodal projection file, while other configured local engines use the standard model repository. |

**Observed / reported:** component names and asset paths are in the registry; model-specific details are documented in the project's model-assets notes. The GGUF repository is under a different publisher account from the main VLM repository. Model weights are external downloads and were not inspected.[^mineru-repo]

## Runtime selection

**Observed:** explicit `onnx` or `torch` selects the small-model backend; `auto` selects Torch only if its required modules are importable and the selected device is not CPU, otherwise ONNX. Layout, OCR and formula ONNX sessions use CPU. Table ONNX sessions independently attempt CUDA when available, with CPU fallback; their thread defaults are four intra-op and one inter-op unless overridden.[^mineru-repo]

**Observed:** VLM choices include llama.cpp, vLLM, LMDeploy and explicit MLX. Auto chooses llama.cpp on CPU or non-Linux/Windows, prefers vLLM on Linux with a non-CPU device when available, then eligible LMDeploy, otherwise llama.cpp. A configured VLM server URL takes precedence over local engines. This is separate from uploading a document to the remote parse API.[^mineru-repo]

**Reported:** `model.source` supports automatic, Hugging Face, ModelScope and local operation. The registry actually declares both Hugging Face and ModelScope, despite a model-assets note stating that only Hugging Face is configured; the note is not an accurate description of this snapshot's registry. A remote VLM does not require local VLM weights.[^mineru-repo]

## Operational boundaries and limits

Configured remote VLM inference may transmit page images to its server; optional LLM-aided processing is another external-content boundary. The README states documents are not automatically uploaded to the official parse service, not that all network traffic is absent. The code also includes a telemetry signing credential; its value and live status are not reproduced or verified here. Runtime behavior, provider availability, download integrity, performance and model quality were not tested. Model assets and external DocVortex and engine internals are outside this static partial review.[^mineru-repo]

## Relationships

- **Uses:** [MinerU2.5-Pro](mineru2-5-pro.md), whose model-family evidence is documented separately.[^mineru-repo]
- **Supports:** [MinerU 4 OCR pipeline](mineru-4-ocr-pipeline.md), with specialized local components and optional VLM inference.
- **Related to:** [PP-OCRv6](pp-ocrv6.md) and [PP-DocLayoutV2](pp-doclayoutv2.md), which describe the model families.

[^mineru-repo]: [MinerU repository README](../raw/MinerU/README.md), “MinerU 4.0” and “Model Engines with Extras”; `mineru/model/registry.py::MINERU_4_MODELS_ONNX`, `::MINERU_4_MODELS_TORCH`, `::MINERU_2_5_PRO_2605_1_2B_GGUF`, `::model_repos_for_tier`; `mineru/model/runtime/device.py::resolve_small_model_backend`; `mineru/model/runtime/onnx.py::ort_providers`, `::table_ort_session`, `::configure_ort_threads`; `mineru/model/vlm/selector.py::resolve_vlm_engine`; `mineru/model/vlm/client.py::get_vlm_predictor`; `docs/next/model-assets.md` §§“下载与离线运行”, “资源结构”; `docs/en/usage/model_source.md` §“Three remote connections at a glance”; `mineru/doclib/telemetry/transport.py::signed_headers`; revision `b7f3dd0c5f6e6d66a298239ffd02b328b873918e`.
