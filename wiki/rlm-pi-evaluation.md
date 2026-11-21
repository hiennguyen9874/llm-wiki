---
type: Concept
title: rlm.pi evaluation
description: Project-reported OOLONG results and protocol limits for the rlm.pi plugin.
tags: [language-models, evaluation, long-context]
status: draft
created: 2026-11-21
generated: { by: llm-wiki-agent/1, at: 2026-11-21T17:01:33Z }
sources:
  - id: rlm-pi
    resource: ../raw/rlm.pi/README.md
    scope: ../raw/rlm.pi/
    kind: code
    revision: cc77fab30d085d1207eeb6ee7a242facb95f6061
    title: rlm.pi
---

The [rlm.pi plugin](rlm-pi-implementation.md) reports OOLONG-synth results for 24 tasks at up to 65,536 context tokens and temperature 0. These are project-reported, not independently verified or directly comparable to other [RLM benchmarks](rlm-evaluation.md) without aligning tasks, models, budgets and scoring.[^rlm-pi]

## Reported results

| Model | Full-correct tasks | Approximate tokens per task |
| --- | ---: | ---: |
| `zai/glm-5.3` | 23/24 (95.8%) | 28k |
| `b-ai/qwen3.8-27b` | 22/24 (91.7%) | 37k |
| `openrouter/google/gemma-4-31b-it:free` | Pending | — |

The README reports approximately zero dollars per task with an asterisk, but does not explain that asterisk in the inspected text; do not treat it as a general deployment price. The benchmark README says the synthetic-record aggregation grader scores 0–1 and marks a task correct only at a full score. It describes engine runs with real providers and Python, `maxIterations=200`, token budgeting disabled, unlimited concurrency and five retries; these benchmark settings differ from the inspected interactive defaults. Dataset download, model/provider conditions, selection, run journals, scoring implementation, variance and reproducibility have not been independently checked. **Reported.**[^rlm-pi]

## Source and coverage

Static inspection covers the root and benchmark READMEs and plugin defaults; benchmark code, panel configuration, results, archived journals and chart are inventoried but pending. No benchmark, model call, or data download was run. The reported scores and costs are not independently verified; draft status records the outstanding coverage.[^rlm-pi]

[^rlm-pi]: [Repository README](../raw/rlm.pi/README.md), “Benchmarks”; `bench/README.md`, “Suite”, “Run”, “Results”, and “Engine settings”; `pi-plugin/rlm/src/config/defaults.ts::DEFAULT_CONFIG`.
