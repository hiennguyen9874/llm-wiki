---
type: SourceMap
title: GBrain source map
description: Coverage ledger for the GBrain repository snapshot, listing every top-level artifact as inspected, sampled, excluded or pending so future ingests can be idempotent.
tags: [agent-memory, gbrain, source-map, coverage]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:00:00Z }
sources:
  - id: readme
    resource: ../raw/gbrain/README.md
    scope: ../raw/gbrain/
    kind: code
    revision: 27f8b9d
    title: GBrain README (repository root)
  - id: version
    resource: ../raw/gbrain/VERSION
    kind: code
    revision: 27f8b9d
    title: GBrain VERSION file
---

This is the coverage ledger for the [GBrain](gbrain-overview.md) ingest. The source identity is the scope `raw/gbrain/` (a git submodule) at revision `27f8b9d`, version `0.60.593.0`, entry point `README.md`.[^readme][^version] The repository is far too large to read exhaustively (about 13k files outside `.git`), so the ledger records what each top-level item contributed and what remains pending. File counts below were taken by the curator with `find … -type f | wc -l` at the snapshot.

## Ledger

| Artifact | Files | Status | Where it landed / why excluded |
| --- | --- | --- | --- |
| `README.md`, `VERSION`, `LICENSE`, `package.json` | 4 | inspected | [Overview](gbrain-overview.md) |
| `AGENTS.md`, `CLAUDE.md` | 2 | inspected (partial: first ~200 and ~250 lines) | [Architecture](gbrain-architecture-and-engines.md), [data model](gbrain-data-model-and-system-of-record.md) |
| `DESIGN.md` | 1 | inspected; it is the admin-SPA design system, not product architecture | [CLI and MCP surface](gbrain-cli-and-mcp-surface.md) (admin note) |
| `SECURITY.md` | 1 | inspected in full | [Authorization and security](gbrain-authorization-and-security.md) |
| `CONTRIBUTING.md`, `docs/TESTING.md`, `docs/RELEASING.md`, `docs/ci-*.md` | 5 | inspected (sections) | [Testing, CI and release](gbrain-testing-ci-and-release.md) |
| `BOOTSTRAP_FOR_AGENTS.md`, `INSTALL_FOR_AGENTS.md`, `openclaw.plugin.json` | 3 | inspected | [Recipes, plugins and bootstrap](gbrain-recipes-plugins-and-bootstrap.md) |
| `CHANGELOG.md` (4.8 MB, 987 entries) | 1 | head ~120 lines only; remainder pending | release conventions only |
| `TODOS.md` (880 KB), `llms.txt`, `llms-full.txt` | 3 | head of TODOS only; llms files excluded as generated doc maps | — |
| `dbg-tmp.ts` | 1 | inspected; stale root script with a hard-coded absolute path | [Testing, CI and release](gbrain-testing-ci-and-release.md) |
| `docs/` | 1,442 | sampled by topic: architecture (109), guides (111), mcp (18), protocol, ethos, tutorials, integrations | most cluster pages |
| `docs/eval/` | 986 | 887 are `system-one/` runners and datasets: excluded as bulk instrument data; headline result docs sampled | [Evals and benchmarks](gbrain-evals-and-benchmarks.md) |
| `docs/designs/`, `plans/`, `proposals/`, `research/`, `incidents/`, `fix-wave-notes/`, `test-audit/` | ~140 | titles only, a few headings read; pending | — |
| `src/` | 3,549 | targeted reads: `core/engine.ts`, `operations.ts`, `schema.sql`, `core/search/*`, `core/minions/*`, `core/cycle*`, `cli/*`, `mcp/*`, `core/access/*` headers. Most of `src/core` (588 entries) and `src/commands` (277 top-level entries) not read | most cluster pages |
| `skills/` | 236 (75 skills) | manifest parsed; ~18 `SKILL.md` heads read | [Skills and resolver](gbrain-skills-and-resolver.md) |
| `recipes/` | 69 | 10 recipe files' frontmatter and intros | [Recipes, plugins and bootstrap](gbrain-recipes-plugins-and-bootstrap.md) |
| `plugin/`, `plugin-variants/` | 139 / 125 | generated plugin trees; READMEs and manifests only | same |
| `templates/`, `examples/` | 28 / 13 | read | same |
| `admin/` | 33 | nature and pages inspected; committed `admin/dist` excluded as build output | [Authorization and security](gbrain-authorization-and-security.md) |
| `evals/` | 518 | READMEs, ledger and baseline read; fixtures excluded | [Evals and benchmarks](gbrain-evals-and-benchmarks.md) |
| `scripts/` | 436 | grouped by name; headers of a few read | [Testing, CI and release](gbrain-testing-ci-and-release.md) |
| `test/`, `tests/` | 7,244 / 20 | organization and counts only; bodies excluded | same |
| `spec/` | 7 | TLA+ README and drain-lease spec described | same |
| `vendor/`, `patches/`, `native/`, `third-party/` | 40 / 1 / 22 / 2 | READMEs and licenses; vendored driver and prebuilt binaries not audited | same |
| `tools/` | 1 | listed only (`inspect-sql-grammar.ts`) | — |
| `.github/workflows/` (23) | 23 | listed and named | [Testing, CI and release](gbrain-testing-ci-and-release.md) |

## Idempotency notes

- Every GBrain concept cites `../raw/gbrain/README.md` as the entry point and declares the same revision. A re-ingest at the same revision should be a no-op unless it targets a "pending" row above.
- A newer revision of the submodule is a new snapshot: re-check time-sensitive defaults (embedding and reranker models, mode bundles, counts) listed in [Doc/code discrepancies](gbrain-doc-code-discrepancies.md) and the `stale_after` pages.
- Execution performed: no GBrain tests or builds. Privacy screening was limited to the sampled files; the uninspected remainder has not been screened. Only environment-variable names and redacted descriptions were intentionally compiled.

[^readme]: `README.md` (entry point of the package scope `raw/gbrain/`).
[^version]: `VERSION` → `0.60.593.0`; `git -C raw/gbrain log -1 --format=%h` → `27f8b9d`.
