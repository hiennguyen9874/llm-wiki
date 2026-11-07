---
type: Concept
title: GBrain evals and reported benchmarks
description: The eval suites shipped with GBrain, what each measures, and every headline number with its protocol, locator and evidence class (almost all Reported, not reproduced here).
tags: [agent-memory, gbrain, evals, benchmarks, longmemeval]
status: draft
created: 2026-11-06
stale_after: 2027-02-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:00:00Z }
sources:
  - id: readme
    resource: ../raw/gbrain/README.md
    scope: ../raw/gbrain/
    kind: code
    revision: 27f8b9d
    title: GBrain README (repository root)
  - id: retrieval-doc
    resource: ../raw/gbrain/docs/architecture/RETRIEVAL.md
    kind: code
    revision: 27f8b9d
    title: Retrieval architecture
  - id: eval-bench
    resource: ../raw/gbrain/docs/eval-bench.md
    kind: code
    revision: 27f8b9d
    title: Eval bench guide
  - id: brainbench-doc
    resource: ../raw/gbrain/docs/eval/BRAINBENCH.md
    kind: code
    revision: 27f8b9d
    title: BrainBench documentation
  - id: brainbench-baseline
    resource: ../raw/gbrain/evals/brainbench/baselines/main.json
    kind: code
    revision: 27f8b9d
    title: BrainBench committed baseline
  - id: take-grading
    resource: ../raw/gbrain/evals/take-grading/README.md
    kind: code
    revision: 27f8b9d
    title: Take-grading eval
  - id: time-aware
    resource: ../raw/gbrain/docs/eval/TIME_AWARE_RETRIEVAL_RESULTS.md
    kind: code
    revision: 27f8b9d
    title: Time-aware retrieval results
  - id: answer-packet
    resource: ../raw/gbrain/docs/eval/ANSWER_PACKET_RESULTS.md
    kind: code
    revision: 27f8b9d
    title: Answer packet results
  - id: search-modes
    resource: ../raw/gbrain/docs/guides/search-modes.md
    kind: code
    revision: 27f8b9d
    title: Search modes guide
---

GBrain documents many benchmark results, but a recurring finding is that **the retrieval-quality numbers cannot be reproduced from artifacts committed in this repository**: the headline R@5, P@5 and LongMemEval figures come from a sibling `gbrain-evals` repository or runs recorded in prose. A subagent searched the checkout and found `evals/longmemeval/` holding only a dev-slice seed list and split file, and `evals/brainbench/baselines/main.json` holding fixtures hash, suite names and a justification string but no R@5/P@5 values; the number `0.6626` matched only docs. Treat every number below as **Reported** unless stated.[^retrieval-doc][^brainbench-baseline] The pipeline these numbers describe is in [retrieval pipeline](gbrain-retrieval-pipeline.md) and [knowledge graph](gbrain-knowledge-graph.md).

## Retrieval benchmarks (Reported)

| Claim | Number | Protocol | Locator |
| --- | --- | --- | --- |
| Relationship retrieval one switch | mean R@5 **0.6626 → 0.7241** (45 of 435 question runs better, 0 worse) | 145 synthetic BrainBench relationship questions, 3 ingestion orders, gbrain v0.48.4.0, external refresh 2026-09-09 | `RETRIEVAL.md` "The benchmark"; `README.md` |
| Whole-system adapters (mean P@5 / R@5) | graph-oracle-parse 0.3421 / 0.9791 (upper bound); reference hybrid 0.1917 / 0.6874; keyword 0.1710 / 0.6244; vector 0.1076 / 0.4069 | 240-page generated corpus | `RETRIEVAL.md` table |
| Retired headline | P@5 49.1%, "+31.4 pts" — marked **"do not cite"** | metric helpers since corrected | `RETRIEVAL.md` |
| Reranker | reshuffles 60% of top-1 (20 queries, hosted reranker, not Voyage); 60% lower cost at 50 candidates × 1,400 tokens | gbrain-evals #148 | `RETRIEVAL.md`, `search-modes.md` |
| Relational re-pin | hit@1 21/39 → 3/39 with rerank on and unpinned; 0 losses with pin = 3 | 39-question NamedThingBench fixture | `RETRIEVAL.md` |
| LongMemEval-S strict `recall_all@5` | **449/470 = 95.53%** release default; 439/470 = 93.40% reranker-off | cleaned S split, k = 5, measured 2026-09-06 at v0.48.4.0 | `eval-bench.md`; `RETRIEVAL.md` |
| Expansion harm | plain 93.19% vs equal-weight expansion 54.89%; budget 0.25 → 394/470 | 470 scored questions, 2026-09-02 receipt | `RETRIEVAL.md` |
| Expansion latency | p50 2,022 → 227 ms with strict recall@10 298 vs 299 of 300 | 300 questions, 2026-10-14 | `search-modes.md` |
| Autocut | 449/470 → 379/470; window 3,256 → 1,633 tokens | pre-registered rule R2 | `RETRIEVAL.md` |
| `metadata_boost_gate` | nDCG@5 53.0 → 57.8 (bare vector 60.5) | held-out conceptual-recall category | `RETRIEVAL.md` |
| BFS walk speedup | depth-5 12-page clique 44–91 ms → 4–9 ms | medians vs v0.60.292.0, `scripts/bench-graph-walk.ts` | `RETRIEVAL.md` |
| Time-aware retrieval | LoCoMo held-out 74.2% → 88.2% (+14.0 pts, CI [+11.8, +16.2]) | date frame in `think` and retrieval arms | `TIME_AWARE_RETRIEVAL_RESULTS.md` |
| Answer-evidence packet (negative result) | 53/60 vs 48/60, zero wins and five losses | presentation experiment, $8.01 | `ANSWER_PACKET_RESULTS.md` |

The README's own number is the 0.6626 → 0.7241 figure and states that 0.9791 is "the `graph-oracle-parse` upper bound, not a product score".[^readme][^eval-bench][^time-aware][^answer-packet]

## Eval suites and gates (Reported unless noted)

| Suite | What it measures |
| --- | --- |
| **BrainBench** | 8 cross-harness memory-conformance suites: know-to-ask, push, write-back, continuity, trust, state-resolution, poisoning, deletion. Zero-gated metrics include `source_isolation_violations`. CI compares HEAD to **main's** committed baseline so a PR cannot bless its own regression (Observed in `ci-brainbench-gate.sh`). Committed ledger: 177 generated + 7 hand-authored fixtures, 29 holdout, seed 42. Baseline: `know_to_ask_failure_rate` 0.00 on three harnesses. |
| **LongMemEval** | Public retrieval benchmark; strict `recall_all@5` over 470 scored questions (500 minus 30 abstention). |
| **Take-grading** | Which chat models may auto-grade a forecasting take at a 0.95 confidence rule; one model reported 496 applied / 0 wrong at $9.25. |
| **Content-repair judgment** | Models allowed to judge `frontmatter_slug_conflict` holds; three qualify; best 92.0% true-duplicate accuracy over 432 pair runs. |
| **Fence-repair Tier 3** | LLM repair of malformed facts/takes fences: best 95/99 gate-pass with 0/99 false-accept; a weaker model fails at 1.8% false-accept. |
| **Pinned-questions benefit gate (B5)** | Lifecycle dollars per correct answer for `pinned` vs `query_reader` vs `think`; no default-on without a win. |
| **takes-bootstrap, forecast-journal, title-mention, functional-area-resolver, harness-instructions** | Instruments for unattended take extraction (thresholds 0.80 precision / 0.70 recall), holder ranking (5,622 predictions pass), title-mention retrieval and resolver compression. |

Capture-and-replay: contributor mode (`GBRAIN_CONTRIBUTOR_MODE=1` or `eval.capture`) records `eval_candidates`, exports NDJSON (`schema_version: 1`), and `gbrain bench publish` plus `gbrain eval gate` compare runs. `docs/eval/` has 986 files, 887 under `system-one/`; 82 `test/eval*` files pin the instruments keylessly (Observed counts by subagent).[^brainbench-doc][^take-grading][^eval-bench]

## Caveats

- Numbers are time-stamped to specific versions (mostly v0.48.4.0 in September 2026) while the snapshot is v0.60.593.0, so they may not reflect current behavior.
- The doc `search-modes.md` itself notes that an old expansion-budget receipt predates page-grain fusion and "no longer helps".
- Self-reported author benchmarks; no independent corroboration was found in this snapshot.[^search-modes]

## Relationships

- Evaluates: [retrieval pipeline](gbrain-retrieval-pipeline.md), [knowledge graph](gbrain-knowledge-graph.md), [memory trust](gbrain-memory-trust-and-egress.md) (calibration).
- Run through: [testing, CI and release](gbrain-testing-ci-and-release.md).
- Part of: [GBrain overview](gbrain-overview.md).

[^readme]: `README.md` bullet "A typed knowledge graph" (R@5 figures and the `graph-oracle-parse` caveat).
[^retrieval-doc]: `docs/architecture/RETRIEVAL.md` "The benchmark", "How to verify", "Multi-query expansion", "Autocut", "Relational re-pin", "Breadth-first graph walks".
[^eval-bench]: `docs/eval-bench.md` "Current measured result", recorded and negative experiments; `docs/eval-capture.md`.
[^brainbench-doc]: `docs/eval/BRAINBENCH.md` (seams, formulas, floors); `evals/brainbench/README.md`, `_ledger.json`; `scripts/ci-brainbench-gate.sh`.
[^brainbench-baseline]: `evals/brainbench/baselines/main.json` (suite list, fixtures hash, justification); `evals/longmemeval/` listing.
[^take-grading]: `evals/take-grading/README.md`; sibling `evals/*/README.md` for the other gates.
[^time-aware]: `docs/eval/TIME_AWARE_RETRIEVAL_RESULTS.md`.
[^answer-packet]: `docs/eval/ANSWER_PACKET_RESULTS.md`.
[^search-modes]: `docs/guides/search-modes.md` (expansion latency; receipt caveat).
