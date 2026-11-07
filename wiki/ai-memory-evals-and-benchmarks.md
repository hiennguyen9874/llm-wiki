---
type: Concept
title: ai-memory evals and LongMemEval-S benchmarks
description: The ai-memory-eval harness subcommands and the published LongMemEval-S retrieval results (3.4.0 hit@5 0.951 FTS / 0.940 local), with protocol, trend and caveats.
tags: [agent-memory, ai-memory, evals, benchmarks, longmemeval]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
stale_after: 2027-02-06
sources:
  - id: readme
    resource: ../raw/ai-memory/README.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory README
  - id: bench-340
    resource: ../raw/ai-memory/docs/benchmarks/longmemeval-s-3.4.0-release.md
    scope: ../raw/ai-memory/docs/benchmarks/
    kind: dataset
    revision: 26fa9cf
    title: LongMemEval-S 3.4.0 release report
  - id: bench-readme
    resource: ../raw/ai-memory/docs/benchmarks/README.md
    scope: ../raw/ai-memory/docs/benchmarks/
    kind: dataset
    revision: 26fa9cf
    title: Benchmarks README
  - id: retrieval-ab
    resource: ../raw/ai-memory/docs/benchmarks/retrieval-ab-r2.md
    scope: ../raw/ai-memory/docs/benchmarks/
    kind: dataset
    revision: 26fa9cf
    title: Retrieval A/B R2
  - id: fidelity
    resource: ../raw/ai-memory/docs/benchmarks/consolidation-literal-fidelity-2026-10-15.md
    scope: ../raw/ai-memory/docs/benchmarks/
    kind: dataset
    revision: 26fa9cf
    title: Consolidation literal fidelity report
  - id: evals-readme
    resource: ../raw/ai-memory/evals/README.md
    scope: ../raw/ai-memory/evals/
    kind: code
    revision: 26fa9cf
    title: evals README
---

# ai-memory evals and LongMemEval-S benchmarks

ai-memory ships an in-repo evaluation harness (`ai-memory-eval`) and publishes retrieval-quality numbers with provenance, reproducible from that harness.[^bench-readme][^evals-readme] The README lists the benchmarks folder among its user-facing docs.[^readme] All numbers below are **Reported** by the project from its own runs (the 3.4.0 report was read in full directly this session; other reports via delegated reading); they were **not reproduced** here.

## Harness subcommands

`ab` (live two-provider A/B on the consolidation batch request, fidelity-scored), `projection` (zero-LLM: which fixture facts reach the prompt), `retrieval` (starts a real `ai-memory serve`, replays hooks, runs `memory_query`; metrics hit@k, recall@k, recall-all@k, latency and context tokens; `--qa` LLM judge, `--embeddings local`, `--no-embedding-cache`, `--stratify`, `--engine grep`, `coding-v1` corpus), `retrieval-compare` (two saved reports) and `abstention` (offline answerability + threshold sweep). Fixtures: seven session logs (`01`–`07`, including pt-BR tail forms and injection traps), `abstention/v1.json`, `retrieval/coding-v1.json`. `evals/README.md` says "four subcommands" — five exist.[^evals-readme]

## LongMemEval-S, release 3.4.0 (2026-11-04)

Protocol: code `7bb659ce` (the `release: v3.4.0` commit), dataset `longmemeval_s` (sha256 `08d8dad4be43ee20…`), 470 scored questions (30 abstention excluded, per delegated reading of the benchmarks README), AMD Ryzen 9 7950X3D 32 threads **under load** (load average ~25–55), `--concurrency 6 --http-timeout-secs 900`, observation stream on, wiki checkpoints skipped; the local run used `--no-embedding-cache`.[^bench-340]

| Mode | hit@1 | hit@3 | hit@5 | hit@10 | recall@5 | recall@10 | p50 | p95 | ctx tokens |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FTS 3.4.0 | 0.857 | 0.928 | 0.951 | 0.972 | 0.892 | 0.936 | 15 ms | 114 ms | 518.6 |
| local 3.4.0 | 0.764 | 0.906 | 0.940 | 0.972 | 0.876 | 0.941 | 129 ms | 307 ms | 519.6 |

FTS equals 3.3.3 at every cutoff; local hit@5 moved 0.943 → 0.940, inside the stated ±0.005 overall noise band; small slices vary ±0.02–0.03.[^bench-340]

**Trend** (delegated reading of the release reports): 2.0 (2026-09-01) FTS 0.617 / local 0.823 hit@5 → 3.0.0, where the observation stream became default, FTS 0.951 / local 0.945 → FTS flat at 0.951 through 3.4.0, local oscillating 0.938–0.949.[^bench-readme]
**A/B R2** (2026-09-21, 2.4 RC): FTS → local hit@5 0.666 → 0.815 (+0.149) at +89 ms p50.[^retrieval-ab]
**Consolidation fidelity** (2026-10-15, three runs/side): projection loss 8/15 → 3/15 on generated fixtures and 1/3 → 0/3 on pt-BR; parse rate and inventions unchanged.[^fidelity]

## Caveats

Small stratified slices are noisy; embedding caches inflate speed so release numbers must be cold; wall-clock ingest follows host load; local run-to-run variation is tracked upstream; competitor benchmarks are incomparable (the project's own comparison declines to rank).[^bench-340][^bench-readme] See [Comparison claims](ai-memory-comparison-claims.md).

## Relationships

- Evaluated system: [Retrieval pipeline](ai-memory-retrieval-pipeline.md). Gate use in [Auto-improvement](ai-memory-auto-improvement.md).
- Embedder: [Providers](ai-memory-llm-and-embedding-providers.md).

[^readme]: `../raw/ai-memory/README.md` — "Docs" table row for `docs/benchmarks/`.
[^bench-340]: `../raw/ai-memory/docs/benchmarks/longmemeval-s-3.4.0-release.md` — "Setup" (commit, dataset sha, hardware, commands) and "Results" tables (read directly).
[^bench-readme]: `../raw/ai-memory/docs/benchmarks/README.md` — dataset definition, trend and caveats (delegated reading; heading-level locators).
[^retrieval-ab]: `../raw/ai-memory/docs/benchmarks/retrieval-ab-r2.md` — A/B results (delegated reading).
[^fidelity]: `../raw/ai-memory/docs/benchmarks/consolidation-literal-fidelity-2026-10-15.md` — results table (delegated reading).
[^evals-readme]: `../raw/ai-memory/evals/README.md`; `evals/src/main.rs` subcommand definitions.
