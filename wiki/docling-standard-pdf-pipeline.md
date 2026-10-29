---
type: Concept
title: Docling standard PDF pipeline
description: Docling's standard PDF pipeline combines threaded layout, selective OCR, table reconstruction, and reading-order assembly into a structured document.
tags: [ml, docling, document-parsing, ocr, pipeline]
status: draft
created: 2026-10-29
generated: { by: llm-wiki-agent/1, at: 2026-10-29T06:58:04Z }
stale_after: 2027-04-29
sources:
  - id: docling-repo
    resource: ../raw/docling/README.md
    scope: ../raw/docling/
    kind: code
    revision: 8f7ae54
    title: Docling repository
---

# Docling standard PDF pipeline

**Observed:** At the cited revision, Docling's default PDF conversion uses a threaded parser backend and a multi-stage pipeline that combines native PDF content, layout predictions, selective OCR, table reconstruction and document assembly. Image input uses the same pipeline with an image backend.[^docling-repo]

## Stages and defaults

The actual queue wiring is **preprocessing → layout → OCR → layout postprocessing → table structure → optional form fields → page assembly**. Document assembly then applies reading order and optional heading hierarchy; optional enrichment includes code and formulas.[^docling-repo]

OCR and table structure are enabled by default; the default layout option is Heron and OCR uses automatic engine selection. The stage batch sizes default to four pages, with bounded inter-stage queues. Image export and form-field extraction are off by default; page rendering can still be required internally.[^docling-repo]

## OCR region and text-layer policy

- **PDF-aware layout regions** are the current `DEFAULT`: select layout regions needing OCR based on native text, bitmap and shape evidence; merge with PDF text taking priority over overlapping OCR cells.
- **Layout regions** OCR layout detections and give OCR cells priority. **Full page** OCR replaces the ordinary extracted text layer. A separate option can replace a detected broken text layer with full-page OCR while retaining invisible cells.
- OCR crops use a default scale of 3.0, equivalent to 216 dpi at 72 points per inch. The result can include a mean OCR-cell confidence; it is not a guarantee of transcription correctness.[^docling-repo]

## Automatic OCR selection and operational risk

**Observed:** Automatic selection tries ocrmac on macOS or Nemotron on Linux where eligible, then RapidOCR with ONNX Runtime, EasyOCR, and RapidOCR with Torch. Tesseract is not in this auto-selection sequence. If no candidate is available and no language rejection occurred, the code warns and passes pages through unchanged rather than raising; a successful conversion status alone therefore does not establish that OCR ran. A language rejection produces an aggregated language error instead.[^docling-repo]

The KServe v2 OCR engine sends page crops to an inference endpoint and requires explicit `enable_remote_services`. Its gRPC configuration defaults to TLS off, so deployments must deliberately configure transport protection. Local model downloads and source URL fetching are separate network considerations; the remote-service switch is not a blanket offline guarantee.[^docling-repo]

## Coverage and limits

This is a **partial, static repository ingest** at the pinned revision, not a performance or runtime verification. Inspected: README, documentation inventory, converter, standard pipeline, OCR selection and merging, configuration, VLM runtime and selected tests/docs via parallel exploration. External `docling-core`, `docling-parse`, third-party engines and model weights were not inspected. Other format backends, ASR/video, deployment and most examples/tests remain pending. Binary fixtures, decorative assets, generated lockfile and historical changelog were excluded from this focused pass; no model inference, downloads or tests were run. The repository's MIT code license does not automatically establish the license of each model.[^docling-repo]

## Relationships

- **Uses:** [Docling OCR engines](docling-ocr-engines.md) for interchangeable recognition backends.
- **Uses:** [Docling document representation](docling-document-representation.md) as its assembled output.
- **Related to:** [Docling models and inference engines](docling-models-and-inference-engines.md), an alternative VLM conversion path and shared engine architecture.
- **Related to:** [Docling architecture](docling-architecture.md), the converter/backend overview.

[^docling-repo]: Docling repository, revision `8f7ae54`: `README.md` §Features, §License; `docling/document_converter.py::PdfFormatOption`, `ImageFormatOption`; `docling/pipeline/standard_pdf_pipeline.py::StandardPdfPipeline._create_run_ctx`, `_init_models`; `docling/datamodel/pipeline_options.py::PdfPipelineOptions`, `OcrOptions`; `docling/models/base_ocr_model.py::BaseOcrModel.get_ocr_rects`, `_find_pdf_aware_layout_ocr_rects`, `post_process_cells`; `docling/models/stages/ocr/auto_ocr_model.py::OcrAutoModel`; `docling/models/stages/ocr/kserve_v2_ocr_model.py::KserveV2OcrModel.__init__`; `docling/datamodel/kserve_v2_options.py::KserveV2OptionsMixin`.
