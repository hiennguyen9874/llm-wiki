---
type: Concept
title: Marker deployment and configuration
description: Marker exposes CLI, Python, and demonstration server interfaces with shared inference, configurable LLM egress, and deployment-specific security limits.
tags: [ml, ocr, deployment, security]
status: draft
created: 2026-11-08
stale_after: 2027-05-08
generated: { by: llm-wiki-agent/1, at: 2026-11-08T03:10:11Z }
sources:
  - id: marker-repo
    resource: ../raw/marker/README.md
    scope: ../raw/marker/
    kind: code
    revision: 71dd5fd7e51ab24f8624b6ba2fcb6014b4e40ed4
    title: Marker repository
---

# Marker deployment and configuration

**Observed:** `marker-pdf` 2.1.0 declares Python 3.10–3.x and CLI entry points for single-file conversion, batches, a GUI and a server. Optional non-PDF dependencies are in the `full` extra. [Marker](marker.md) selects a device-based default mode, and can be configured through its Python API and CLI.[^marker-repo]

## Batch and configuration

**Observed:** The batch command starts or attaches a shared Surya inference server unless OCR is disabled, then uses worker processes. When `SURYA_INFERENCE_PARALLEL` is unset, it budgets per-worker concurrency based on server capacity; an explicit value bypasses this automatic budget. It enumerates files with unsorted `os.listdir` before slicing into shards, so independent machines with different directory orders can overlap or miss inputs. The code forces `disable_multiprocessing` for nested work but still starts a process pool: the README's claim that this option runs everything in one process does not describe this batch implementation.[^marker-repo]

**Observed:** `assign_config` applies attributes recognized by the target class, including class-prefixed settings; unrecognized keys are ignored. Confirm effective settings rather than assuming a misspelled key fails validation.[^marker-repo]

## Security and external services

**Observed:** Optional LLM services accept prompts and document images; the default service is Gemini. OpenRouter's service defaults `openrouter_allow_data_collection` to true, allowing routing to providers without zero data retention. Review the selected provider's current terms and the document's sensitivity before enabling external services.[^marker-repo]

**Observed:** The demonstration FastAPI server accepts a server-side file path and writes uploaded files using the supplied filename; the inspected routes do not implement authentication or filename sanitization. **Synthesis:** Do not expose it to untrusted clients without independent hardening and access controls. Its API exposes only a subset of conversion options, not `use_llm` or `disable_ocr`.[^marker-repo]

Static inspection only; no service, network call, exploit, test suite or model was run. Third-party service behavior, authorization, retention guarantees and uninspected deployment components remain unverified.[^marker-repo]

## Relationships

- **Uses:** [Marker conversion pipeline](marker-conversion-pipeline.md) for the local processing stages.
- **Related to:** [Marker document representation](marker-document-representation.md), which describes the output formats returned by these interfaces.

[^marker-repo]: Datalab, *Marker repository*, revision `71dd5fd`: `pyproject.toml::[project]`, `[project.scripts]`; `marker/converters/pdf.py::PdfConverter.__init__`; `marker/scripts/convert.py::convert_cli`; `marker/config/parser.py::ConfigParser`; `marker/util.py::assign_config`; `marker/services/openrouter.py::OpenRouterService`; `marker/scripts/server.py::CommonParams`, `convert_pdf`, `convert_pdf_upload`; README §§ Usage, Convert multiple files, LLM Services, API server.
