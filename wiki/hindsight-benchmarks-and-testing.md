---
type: Concept
title: Hindsight benchmarks, evals and test suites
description: Hindsight's published benchmark claims and their provenance, the in-repo system evals, blackbox system tests and other test suites.
tags: [agent-memory, hindsight, benchmarks, evals, testing]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
sources:
  - id: readme
    resource: ../raw/hindsight/README.md
    scope: ../raw/hindsight/
    kind: code
    revision: eb963cb
    title: Hindsight README (monorepo root)
  - id: amb-blog
    resource: ../raw/hindsight/hindsight-docs/blog/2026-03-23-agent-memory-benchmark.mdx
    kind: article
    revision: eb963cb
    title: "Agent Memory Benchmark: A Manifesto"
  - id: beam-blog
    resource: ../raw/hindsight/hindsight-docs/blog/2026-04-02-beam-sota.md
    kind: article
    revision: eb963cb
    title: Hindsight Is #1 on BEAM
  - id: evals-readme
    resource: ../raw/hindsight/hindsight-system-evals/README.md
    kind: documentation
    revision: eb963cb
    title: hindsight-system-evals README
  - id: system-tests
    resource: ../raw/hindsight/hindsight-system-tests/pyproject.toml
    kind: code
    revision: eb963cb
    title: hindsight-system-tests package
---

Hindsight's headline claim is state-of-the-art accuracy on long-term-memory benchmarks, but every number in the tree is vendor-published; no independent third-party reproduction is cited in the repo beyond the README's statement about Virginia Tech and Washington Post collaborators. This page is `draft` because none of the figures were re-run.[^readme]

## Published claims (Reported, vendor)

| Benchmark | Reported value | Source locator |
| --- | --- | --- |
| LongMemEval | 94.6% | AMB manifesto results table[^amb-blog] |
| LoComo | 92.0% | same[^amb-blog] |
| PersonaMem / LifeBench | 86.6% / 71.5% | same[^amb-blog] |
| BEAM 10M tokens | 64.1% vs next-best 40.6% (labelled Honcho); RAG baseline 24.9% | BEAM post table[^beam-blog] |
| BEAM 100K / 500K / 1M | 73.4 / 71.1 / 73.9 | same[^beam-blog] |

The AMB post says its numbers are Hindsight's own re-runs at v0.4.19 using the same harness, and argues LoComo/LongMemEval no longer discriminate because long-context stuffing scores competitively.[^amb-blog] The docs warn that vendor roundups self-rank and that a memory system "swings several points across LLMs" (curator note from subagent read of two blog posts; not re-read). The README chart dates from January 2026; live results are published at benchmarks.hindsight.vectorize.io.[^readme]

## In-repo system evals (`hindsight-system-evals/`)

Blackbox quality evals against a real `hindsight-api` and a real model, judged by an independent model that must differ from the model under test (Observed).[^evals-readme]

- Suites: retain (35 capability cases), recall (19 cases over a ~300-memory haystack), consolidation, reflect, refresh-pages. Run with `uv run pytest evals` after setting `HINDSIGHT_EVAL_LLM_*` and `HINDSIGHT_EVAL_JUDGE_*`.
- **BEIR SciFact** recall benchmark (50 queries, 500 abstracts) with floors such as nDCG@10 ≥ 0.83 and recall@10 ≥ 0.88; measured nDCG@10 ≈ 0.874–0.887 per the test comments.
- README-recorded ranker comparison: local cross-encoder 6/19, RRF 10/19, decision model 19/19 (Reported by the README; model names reflect the snapshot). Retain pass rates range from 35/35 for the best model to ~26–27/35 for the weakest listed.
- LoComo, LongMemEval, BEAM, PersonaMem are **not** in-repo; they run via the external AMB project (`run-amb`).
- No committed result artifacts; numbers live in README prose and comments.[^evals-readme]

## Test suites (Observed)

- `hindsight-system-tests/` — 106 blackbox story tests against a stub server (lexical embeddings, no secrets, own pg0 on port 15499); `uv run pytest tests -v`. Required by repo rules for every user-facing capability.[^system-tests]
- `hindsight-integration-tests/` — MCP end-to-end, base-path deployment (Docker + Nginx) and a Hermes embedded smoke test.
- Unit and acceptance suites live in each package; CI layout in [Deployment and CI](hindsight-deployment-and-ci.md).

## Relationships

Efficiency numbers for [decision models](hindsight-decision-models.md) and [consolidation](hindsight-consolidation-and-mental-models.md) come from the same vendor sources. Retrieval design being measured: [Recall](hindsight-recall-pipeline.md).

[^readme]: `README.md` § "Memory Performance & Accuracy".
[^amb-blog]: `hindsight-docs/blog/2026-03-23-agent-memory-benchmark.mdx` (results table around lines 97–98); `blog/2026-08-11-open-source-agent-memory-systems.md` lines 72, 78.
[^beam-blog]: `hindsight-docs/blog/2026-04-02-beam-sota.md` lines 48–62.
[^evals-readme]: `hindsight-system-evals/README.md`; `evals/recall/test_recall.py` lines ~300–342; `hindsight_system_evals/amb.py`.
[^system-tests]: `hindsight-system-tests/pyproject.toml`; `tests/test_NN_*.py`; `hindsight_system_tests/server.py` (`PG0_PORT`).
