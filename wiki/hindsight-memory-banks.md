---
type: Concept
title: Hindsight memory banks
description: Banks as isolated memory stores, with disposition traits, directives, aliases, templates, multilingual behaviour and export/import.
tags: [agent-memory, hindsight, banks, multi-tenancy]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
sources:
  - id: readme
    resource: ../raw/hindsight/README.md
    scope: ../raw/hindsight/
    kind: code
    revision: eb963cb
    title: Hindsight README (monorepo root)
  - id: banks-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/api/memory-banks.mdx
    kind: documentation
    revision: eb963cb
    title: Memory banks API doc
  - id: templates-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/api/bank-templates.mdx
    kind: documentation
    revision: eb963cb
    title: Bank templates API doc
  - id: multilingual-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/multilingual.mdx
    kind: documentation
    revision: eb963cb
    title: Multilingual developer doc
---

A **bank** is an isolated memory store — one "brain" per user, agent or project — holding memories, documents, entities, relationships and directives. Isolation is strict (no cross-bank leakage); each bank has background context, disposition traits and per-bank configuration.[^readme][^banks-doc]

## Semantics (Reported)

- Banks are created automatically on first write; reads of a nonexistent bank return 404.[^banks-doc]
- **Aliases:** extra ids, at most one promoted as display-only `primary`; unique across banks and aliases (409 on collision); not carried by export/import/clone.[^banks-doc]
- **Directives:** hard rules with `name`, `content`, `priority`, `is_active`, `tags`; see [Reflect](hindsight-reflect-agent.md).[^banks-doc]
- **Config** is per-bank over tenant and global defaults (hierarchy in [Storage and configuration](hindsight-storage-and-configuration.md)).[^banks-doc]
- **Transfer:** export/import/clone, and a runbook for splitting a bank in place.[^banks-doc]
- **Per-user isolation inside one bank:** the README suggests custom metadata/tags on retain, filtered at retrieval, as a lighter alternative to one bank per user.[^readme]

## Bank templates

A JSON manifest `version: "1"` with optional `bank` (any per-bank config override), `mental_models` and `directives` provisions a bank in one API call; schema served at `/bank-template-schema.json`, hub at `/templates`.[^templates-doc]

## Multilingual behaviour

Language is detected and preserved end to end (张伟 stays 张伟) and answers follow the query language, bounded by the LLM. The default embedder `BAAI/bge-small-en-v1.5` is English-only — use `BAAI/bge-m3` for other languages; the default reranker covers EN/ES/FR/DE/PT/JA/KO/ZH; `native` BM25 defaults to an `english` dictionary and tokenizes CJK poorly (`HINDSIGHT_API_TEXT_SEARCH_EXTENSION_NATIVE_LANGUAGE`).[^multilingual-doc]

## Relationships

[Retain](hindsight-retain-pipeline.md) writes into banks; [Memory defense](hindsight-extensions-defense-webhooks.md) is a per-bank opt-in policy; the [control plane](hindsight-control-plane.md) and [CLI](hindsight-clients-cli-embed.md) administer banks.

[^readme]: `README.md` § "Memory Banks", "Use Cases → Per-User Memories".
[^banks-doc]: `hindsight-docs/docs/developer/api/memory-banks.mdx` (aliases, directives, config, transfer sections).
[^templates-doc]: `hindsight-docs/docs/developer/api/bank-templates.mdx` (manifest format).
[^multilingual-doc]: `hindsight-docs/docs/developer/multilingual.mdx` (embedding, reranker, BM25 guidance).
