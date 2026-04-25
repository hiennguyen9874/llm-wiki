---
name: llm-wiki-ops
description: Use when applying repo naming conventions, folder placement, index/log updates, or other operational catalog rules for the wiki.
---

# LLM Wiki Ops

Use when updating repo operational conventions and catalog artifacts.
Always activate `llm-wiki-core` first.

This skill owns practical repo-operations conventions.
It does not own privacy judgment or page-schema rules.

## What This Skill Owns
- repo layout reference
- naming conventions
- `wiki/index.md` rules
- `wiki/log.md` rules
- rebuildable catalog stance
- practical operational conventions for durable repo maintenance

## Repository Layout

### `raw/`
- immutable capture layer
- typical homes: inbox, captures, articles, books, papers, web-clips, assets

### `wiki/`
- canonical semantic knowledge
- includes `wiki/index.md`, `wiki/log.md`, `wiki/home.md`, `wiki/overview.md`
- includes `wiki/bases/` and `wiki/canvases/`

### `outputs/`
- durable derived artifacts such as answers, analyses, reports, briefings, crystallizations, ingest plans, and review queue items

## Naming Rules
- use lowercase kebab-case filenames
- name pages by stable concept, entity, project, or topic
- avoid vague prose titles as filenames
- common prefixes may include:
  - `source-`
  - `synthesis-`
  - `compare-`
  - `timeline-`
  - `procedure-`
- Bases live in `wiki/bases/` with `.base`
- Canvases live in `wiki/canvases/` with `.canvas`

## Index as Rebuildable Catalog
- `wiki/index.md` is a required human and agent catalog
- it is useful, but not the source of truth
- source of truth remains actual markdown files, frontmatter, links, and related metadata
- if index drift exists, prefer actual file evidence over stale index rows
- still update index explicitly until better rebuild tooling exists

## `wiki/index.md` Rules
- keep concise and browsable
- include notable pages, bases, canvases, and important artifacts
- update on meaningful writes when discoverability changes

## `wiki/log.md` Rules
- append-only chronological record
- do not rewrite old entries except tiny formatting repairs
- entry format: `## [YYYY-MM-DD] action | Description`

Allowed actions:
- `setup`
- `capture`
- `ingest`
- `query`
- `lint`
- `update`
- `review`
- `research`
- `visualize`
- `crystallize`

Meaningful entries should capture:
- why the change happened
- which important pages or artifacts changed
- whether the change addressed contradiction, retention, privacy, or quality concerns

## Focus Areas
Default domains may include:
1. projects and work
2. research and learning
3. ideas and writing
4. people and relationships
5. health, habits, and personal systems

Keep this lightweight. Strategic priority still belongs in `purpose.md`.

## Interaction With Workflow Skills
- `llm-wiki-ingest`, `llm-wiki-maintenance`, and `llm-wiki-visualization` commonly use this
- `llm-wiki-query` and `llm-wiki-crystallize` use it when saving durable artifacts that affect discoverability or logs
