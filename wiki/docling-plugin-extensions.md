---
type: Concept
title: Docling plugin extensions
description: Docling plugins use Pluggy and package entry points to register additional OCR, layout, or table-structure engines, with third-party plugins requiring explicit enablement.
tags: [docling, plugins, extensibility, ocr, layout-analysis, table-recognition]
status: stable
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T03:17:04Z }
sources:
  - id: docling-plugins-docs
    resource: ../raw/docling-concepts/plugins.md
    title: Docling plugins documentation
---

# Docling plugin extensions

Docling uses Pluggy and package entry points in the `docling` group to let plugins extend pipeline choices. The documented factories register additional OCR, layout, and table-structure engines.[^docling-plugins-docs]

## Registration contract

A package declares a unique plugin name and the module responsible for registration through a setuptools-compatible entry-point mechanism, such as `[project.entry-points."docling"]` in `pyproject.toml` or equivalent Poetry, `setup.cfg`, or `setup.py` configuration.[^docling-plugins-docs]

The plugin module can expose:

- `ocr_engines()`, registering models that implement `BaseOcrModel` and options derived from `OcrOptions`.[^docling-plugins-docs]
- `layout_engines()`, registering models that implement `BaseLayoutModel` and options derived from `BaseLayoutOptions`.[^docling-plugins-docs]
- `table_structure_engines()`, registering models that implement `BaseTableStructureModel` and options derived from `BaseTableStructureOptions`.[^docling-plugins-docs]

## Third-party enablement

External plugins are not enabled by default: a Python configuration must set `PdfPipelineOptions.allow_external_plugins = True` before selecting third-party OCR, layout, or table-structure options. The CLI similarly requires `--allow-external-plugins`; it can list external plugins with `--show-external-plugins` and select the respective engine by name.[^docling-plugins-docs]

## Relationships

- **Extends:** [Docling architecture](docling-architecture.md) by adding selectable pipeline engines.[^docling-plugins-docs]
- **Extends:** [Docling OCR engines](docling-ocr-engines.md) through the OCR-engine factory.[^docling-plugins-docs]

[^docling-plugins-docs]: Docling, [*Plugins*](../raw/docling-concepts/plugins.md) (accessed 2026-08-21).