---
type: Concept
title: Recursive-llm implementation
description: A Python RLM implementation with bounded execution, document citation checks, and an explicitly limited REPL security model.
tags: [language-models, inference, implementation]
status: draft
created: 2026-11-21
generated: { by: llm-wiki-agent/1, at: 2026-11-21T16:48:23Z }
sources:
  - id: grishahq-rlm
    resource: ../raw/grishahq-recursive-llm/README.md
    scope: ../raw/grishahq-recursive-llm/
    kind: code
    revision: a85779a205c60769e1dd8f1c88cc74061d69e89d
    title: Recursive Language Models (recursive-llm)
---

Grigori Gvadzabia's `recursive-llm` is an independent Python implementation of the [recursive language model](recursive-language-models.md) scaffold: it keeps source context in a persistent restricted REPL and lets the model select text, compute, and optionally delegate. The project reports tree-wide budgets, provider portability, run trajectories, and a document mode that checks source citations. These features and their limitations are project-reported unless noted; this review did not execute the library.[^grishahq-rlm]

## Document citation checks

**Reported:** `complete_documents` produces an answer, claims, unknowns and citations against immutable page text. Citations specify document ID, content hash, physical page, zero-based half-open character offsets and exact quote. Search folds case, accents and whitespace but returns original text and offsets. Validation checks identity and quoted spans, **not** whether the quote entails the claim, whether all answer assertions are cited, or whether all relevant facts were found. A PDF text extractor has no OCR and may miss scans or complex tables. Selected text is sent to the configured model; JSONL results can contain answers and quotations even when trajectory content is redacted.[^grishahq-rlm]

**Observed:** `SourceDocument` hashes a version prefix, page count, and length-prefixed UTF-8 page text; its digest is not a hash of the original PDF bytes. Store a separate file hash when binary identity matters.[^grishahq-rlm]

## Security and configuration

**Reported:** the restricted worker, import allowlist, step timeout and optional POSIX resource limits reduce accidental damage but are not a security boundary for hostile or multi-tenant code. The worker runs as the caller; untrusted workloads require stronger isolation such as a hardened container with restricted networking and no host credentials. POSIX limits are opt-in and affect the worker, not provider requests.[^grishahq-rlm]

**Observed:** package metadata declares version 0.6.0, Python >=3.9, MIT licensing, LiteLLM, RestrictedPython and python-dotenv, with optional `pypdf` support. Installation and provider availability were not checked.[^grishahq-rlm]

## Relationships

- **Synthesis:** [Recursive-llm evaluation](recursive-llm-evaluation.md) describes project-reported experiments and their limits.
- **Synthesis:** This is one implementation of [recursive language models](recursive-language-models.md), distinct from the paper authors' implementation.

## Source and coverage

Snapshot at the revision in metadata; upstream is `https://github.com/grishahq/recursive-llm`. Inspected README introduction, package metadata, security policy, document-analysis report, initial `sources.py` and `repl.py`, and portions of benchmark reports. Inventory covers source, tests, examples, benchmarks, experiment captures, CI, visualizer and assets. Remaining README, source modules, tests, benchmarks, examples, CI, visualizer, experiment captures and linked external datasets are pending substantive inspection; binary media and generated recordings have not been reviewed. No code or tests were run, and the source's security claims were not independently validated. Draft status records this incomplete package coverage.[^grishahq-rlm]

[^grishahq-rlm]: [Project README](../raw/grishahq-recursive-llm/README.md), “Why use this implementation?” and “Execution at a glance”; `pyproject.toml` `[project]`; `SECURITY.md` “REPL threat model” and “Optional worker limits”; `DOCUMENT_ANALYSIS.md` “Source identity and search”, “Meaning of a checked result”, and “PDF ingestion and companion”; `src/rlm/sources.py::SourceDocument` and `src/rlm/repl.py::WorkerResourceLimits`.
