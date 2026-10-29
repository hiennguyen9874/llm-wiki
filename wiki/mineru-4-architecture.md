---
type: Concept
title: MinerU 4 architecture
description: MinerU 4 separates document-library and service orchestration from DocVortex native parsing and uses four tiers to route PDF inference into structured document representations.
tags: [ml, ocr, document-parsing, architecture]
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

# MinerU 4 architecture

MinerU 4 is a document-parsing application that combines a local document library, parser services and model inference with DocVortex's separately distributed native document engine. The snapshot provides four request tiers, structured intermediate results and multiple rendering targets; its implementation and the preceding 3.x [MinerU overview](mineru.md) should not be treated as the same API generation. **Observed / reported:** the tier mapping is in code; the division of responsibility is documented by the project.[^mineru-repo]

## Boundaries and flow

**Reported:** DocVortex owns native document parsing, PDF classification and access, deterministic postprocessing and generic rendering; MinerU owns inference, task orchestration and optional LLM enhancement. The conceptual flow is native or OCR/VLM analysis → ModelJson → deterministic postprocessing → MiddleJson → rendering. Its doclib service handles discovery, scheduling, caching and search, while a separate parse server can isolate heavier inference. DocVortex internals are external to this checkout.[^mineru-repo]

**Observed:** public `flash`, `basic`, `standard`, `advanced` map respectively to internal `flash`, `medium`, `high`, `xhigh`. PDF auto mode calls `document.classify()` to select text or OCR; only `flash` with text mode bypasses model initialization entirely. Images are handled via PDF conversion. For the detailed OCR stages see [MinerU 4 OCR pipeline](mineru-4-ocr-pipeline.md).[^mineru-repo]

**Reported:** the `mineru` CLI supports library-based parsing and progressive reading with page/block locators; `mineru-kit parse` is stateless. The README says library active reading defaults to the first 10 PDF pages while stateless parsing defaults to all pages. A remote document parse requires explicit configuration; this is distinct from telemetry and other configured remote inference.[^mineru-repo]

## Coverage and limits

This is a **partial repository ingest** focused on the requested OCR, architecture, models and engines. The README and `docs/` file inventory were inspected; selected architecture, tier and model-asset documentation and PDF/backend/runtime code were inspected statically, including focused test references. The wider doclib, API, router, UI, non-PDF parsers, deployment guides, design decisions and tests remain pending. Local images and integration screenshots are decorative or outside this focus; the chemical-knowledge PDF/XMind are not inspected. Vendored internals, model binaries and external dependencies are not analyzed. No parsing, model download, inference or project tests were executed; package functionality and accuracy are not independently verified. Source is a nested checkout untracked in the parent repository, so preservation across parent checkouts is not established.[^mineru-repo]

## Relationships

- **Uses:** [MinerU 4 OCR pipeline](mineru-4-ocr-pipeline.md) for PDF text and layout inference.
- **Uses:** [MinerU 4 models and inference engines](mineru-4-models-and-engines.md) for independently selected small-model and VLM runtimes.
- **Related to:** [MinerU](mineru.md) retains the older 3.x README evidence.

[^mineru-repo]: [MinerU repository README](../raw/MinerU/README.md), “MinerU 4.0”, “Quick Start” and “Quality Tiers”; `docs/next/architecture.md` §“DocVortex 引擎边界”, §1–2; `mineru/parser/tier.py::_EFFORT_BY_TIER`; `mineru/backend/analysis/pdf/pipeline.py::_prepare_analysis`; `mineru/parser/mineru_parser.py::_prepare_input`; `pyproject.toml::[project]`; revision `b7f3dd0c5f6e6d66a298239ffd02b328b873918e`.
