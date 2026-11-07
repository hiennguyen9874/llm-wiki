---
type: Concept
title: Hy Memory releases, CI, dependencies, tests and security policy
description: Version history highlights, CI and release workflows, dependency extras, test coverage areas, and security reporting policy for the Hy-Memory repo.
tags: [agent-memory, hy-memory, release, ci, testing, security]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:45:29Z }
sources:
  - id: hy-memory
    resource: ../raw/Hy-Memory/README.md
    scope: ../raw/Hy-Memory/
    kind: code
    revision: 9737431
    title: Hy-Memory monorepo (hy-memory 2.0.14, MemHub 1.0.6)
---

# Hy Memory releases, CI, dependencies, tests and security policy

Hy Memory (SDK) and MemHub release independently (`CHANGELOG.md` preamble).[^hy-memory]

## SDK release highlights (`CHANGELOG.md`)

- **Unreleased**: MemHub capture hooks no longer write the DB; they post to `/api/v1/live-capture/{source}`.
- **2.0.14** (2026-11-04): `statuses` filter for explicit `l1_raw` search.
- **2.0.13**: writes fail closed with `agent_error_code`; the store-everything fallback is removed.
- **2.0.12**: configurable intention dedup. **2.0.11**: prompts in 11 languages, per-call `language`. **2.0.10**: `hy_memory.reembed`, `EmbeddingDimensionMismatchError`, pre-trimmed raw. **2.0.9**: placeholder profile values can't supersede. **2.0.8**: `MEMORY_PIPELINE_LOG_ENABLED`, conversation text moved to DEBUG. **2.0.7**: `memory_at` on coding/working memories. **2.0.6**: `search(rerank=False)`. **2.0.5**: extended `get()`, raw retrieval, embedding-service injection, snapshot/restore.
- MemHub: 1.0.0 → 1.0.6 (1.0.1 superseded; 1.0.2 pins `onnxruntime==1.23.2`).

## Dependencies

`requires-python >=3.9`; Apache-2.0; setuptools. Core: pydantic, numpy, openai (≥1.40,<3), python-dotenv, pyyaml, chromadb ≥1.5.9, kuzu, langdetect, scikit-learn, tiktoken, json-repair, rank-bm25, jieba (the last two core on purpose since absence silently degrades lexical search). Extras: `qdrant`, `faiss`, `graph` (neo4j), `mysql`, `rerank` (torch, transformers), `all`, `dev`. No `[project.scripts]`: run the server as `python -m hy_memory.server` (`pyproject.toml`; `MANIFEST.in` prunes tests/docs/scripts/plugins).[^hy-memory] Ruff `target-version = "py38"` vs `requires-python >=3.9` is a mismatch (Synthesis).[^hy-memory]

## CI and release

- `ci.yml` (path-filtered): `sdk` job on ubuntu-24.04/Python 3.12 runs `uv sync --extra dev --extra faiss --extra qdrant` and `pytest tests/`; `memhub` job runs pnpm lint/typecheck/test plus structure/privacy, zero-collection, embedding-model and Core smoke suites. Actions pinned by commit SHA.
- `hermes-provider.yml`: fetches Hermes `agent/memory_provider.py` at a pinned commit, checks SHA-256, then runs `plugins/hermes/tests`.
- `release.yml`: manual only and explicitly **not** used by the current hybrid release (Linux via lifecycle workflow, macOS via Tencent pipeline, assembly manual); stages contract gate → Linux matrix → notarized macOS → public gate → immutable release → post-publish verification → npm publish.
- `linux-lifecycle.yml`: manual runtime lifecycle build/verify with optional draft-release upload.

(`.github/workflows/*.yml`.)[^hy-memory] **Gaps**: no workflow runs the OpenClaw vitest suite, and ruff is never invoked in CI (Observed absence).[^hy-memory]

## Tests

`tests/` holds 112 top-level `test_*.py` plus 26 under `tests/coding/`; pytest `asyncio_mode=auto`, markers `slow`/`integration`, default `-m 'not integration'`; categories (inferred from names): vector-store backends, retrieval/ranking, write path, embedding, L0/profile/intentions, graph (Kuzu/Neo4j), re-embedding, observability/prompts, HTTP server, coding/working. Neo4j tests skip without `HY_TEST_NEO4J_*` and **wipe** `Memory/Topic/VdbRef/User` nodes — use a throwaway instance (`pyproject.toml` `[tool.pytest.ini_options]`; `CONTRIBUTING.md` "Graph backend tests"). Hermes has 37 + 12 tests; OpenClaw uses vitest.[^hy-memory] None were run for this wiki.

## Security policy

`SECURITY.md`: private GitHub Security Advisories only (no email), reports must name SDK vs MemHub, version/commit, repro, impact; fixes target default branch and latest release; no SLA. MemHub specifics defer to `memhub/SECURITY.md` and `PRIVACY.md`. The PR template carries a privacy checklist. The bare SDK HTTP server has no auth — never expose it (`SECURITY.md`; `plugins/hermes/README.md`).[^hy-memory]

## Relationships

- Part of: [Hy Memory overview](hy-memory-overview.md).
- Covers: [plugins](hy-memory-plugins-openclaw-hermes.md), [MemHub apps and release scripts](memhub-apps-and-packages.md), [privacy](memhub-privacy-and-permissions.md).

## Coverage and limits

Static inspection (delegated); test and CI claims come from file names and configs, not execution. `memhub/CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` and `uv.lock` were not summarised beyond the above.

[^hy-memory]: Hy-Memory monorepo, revision 9737431. Locators inline per claim. Evidence class Observed (delegated static inspection, unexecuted) unless labelled otherwise.
