---
type: Concept
title: Docling models and inference engines
description: Docling separates document-conversion model presets from local or remote inference engines, including an automatically selected local VLM runtime.
tags: [ml, docling, vision-language-models, inference, document-parsing]
status: draft
created: 2026-10-29
generated: { by: llm-wiki-agent/1, at: 2026-10-29T06:58:04Z }
stale_after: 2027-04-29
sources:
  - id: docling-repo
    resource: ../raw/docling/README.md
    scope: ../raw/docling/
    kind: code
    revision: 8f7ae54409583908f06a2172d260e71b964cc4dd
    title: Docling repository
---

# Docling models and inference engines

**Observed:** Docling separates a VLM conversion stage and model specification from the engine that executes inference. The VLM pipeline offers a different document-conversion path from the [standard PDF pipeline](docling-standard-pdf-pipeline.md), which composes layout, OCR and table models.[^docling-repo]

## Model versus engine

A model specification carries a repository and revision, prompt, response format, generation settings, supported engines and engine-specific overrides. `VlmConvertModel` creates an engine from the specification and engine options, builds image/prompt inputs and delegates batch prediction. Its MinerU2 path is a notable exception to a simple one-pass page model: it first predicts layout and then recognizes region crops.[^docling-repo]

The VLM pipeline maps model responses back to page documents. Its newer conversion options coexist with a deprecated legacy options path. `force_backend_text` is effective only for DocTags responses in the new path. The default VLM conversion preset is Granite Docling, not a claim that it is the default for the standard PDF pipeline.[^docling-repo]

## Runtime selection

**Observed:** Auto-inline considers MLX on macOS/MPS only when the model explicitly supports it and the runtime is available and sufficiently recent. On CUDA it considers vLLM only when `prefer_vllm` is enabled and support and version checks pass; otherwise it selects Transformers. Separate API engines support remote inference. The engine selection and actual hardware behavior have not been run in this ingest.[^docling-repo]

The VLM stage and model preset system can propagate `trust_remote_code` into the selected engine. Some presets set this explicitly; review the actual preset and its revision rather than assuming that every model load avoids downloaded code. API inference requires the remote-services opt-in; model artifact retrieval is a separate network activity.[^docling-repo]

## Coverage and relationships

**Limit:** Source code and documentation were inspected statically; external model artifacts, third-party runtimes, model accuracy, hardware compatibility and inference behavior were not verified. Wider package coverage is recorded in [Docling standard PDF pipeline](docling-standard-pdf-pipeline.md).[^docling-repo]

- **Uses:** [Granite Docling 258M](granite-docling-258m.md) as one supported conversion-model family.
- **Related to:** [Docling architecture](docling-architecture.md), which explains backend and pipeline dispatch.
- **Related to:** [Docling standard PDF pipeline](docling-standard-pdf-pipeline.md), the modular PDF conversion alternative.

[^docling-repo]: Docling repository, revision `8f7ae54409583908f06a2172d260e71b964cc4dd`: `README.md` §Features, §Quickstart; `docling/datamodel/stage_model_specs.py::VlmModelSpec`, `StagePresetMixin.from_preset`; `docling/datamodel/pipeline_options.py::_default_vlm_convert_options`, `VlmPipelineOptions`; `docling/models/stages/vlm_convert/vlm_convert_model.py::VlmConvertModel`, `_predict_mineru2`; `docling/pipeline/vlm_pipeline.py::VlmPipeline._initialize_new_runtime_system`, `_initialize_legacy_vlm_models`; `docling/models/inference_engines/vlm/auto_inline_engine.py::AutoInlineVlmEngine._select_engine`, `initialize`; `docling/models/inference_engines/vlm/api_openai_compatible_engine.py::ApiVlmEngine.__init__`.
