---
type: Concept
title: CMB — Coding Memory Benchmark
description: Benchmark design and reported results of CMB (long-horizon, interleaved coding-agent memory) and its TriLink method, as shipped as a PDF in the Hy-Memory repo.
tags: [agent-memory, benchmark, coding-memory, evaluation, paper]
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

# CMB — Coding Memory Benchmark

CMB ("A Coding Memory Benchmark for Long-Horizon and Interleaved Coding Agents", submitted to ICLR 2027) evaluates memory mechanisms for coding agents, and proposes **TriLink**, a facts + experience + diff-chain method that corresponds to the SDK's [coding memory](hy-memory-working-coding-memory.md) and [diff chain](hy-memory-coding-diff-chain.md) (`docs/papers/CMB_A_Coding_Memory_Benchmark_for_Long_Horizon_and_Interleaved_Coding_Agents.pdf` Abstract; `README.md::Papers`). All figures below are **Reported** by the paper (text extracted and spot-checked: 216, 750, 5,595, 43.1 appear on pp.1–4, 7); none were reproduced.[^hy-memory]

## Design

- 216 execution-graded code tasks plus 750 diagnostic QA questions over 5,595 turns from 9 repos in 4 languages; 302–928 turns per repo (median 583), 8.23M frozen tokens, 5,377 coding + 218 noise turns, 212 branches, 1,482 decision points of which 1,284 (87%) refer to a non-latest revision (PDF p.1, p.4 §3.2).[^hy-memory]
- Construction: SWE-bench Pro artifacts → file-disjoint task selection → decomposition into points/instructions (3–5 alternatives plus a held-out final request) → round-robin interleaving with noise turns → frozen traces and repo checkpoints replayed identically to every mechanism (pp.3–4 §3.1, Fig. 1).[^hy-memory]
- Grading: task score `y_i = v_i·1[(F2P∪P2P) ⊆ Passed]` (p.4 Eq. 2); QA scored by judge-derived requirement matching (Eq. 3).[^hy-memory]

## Results

- Table 2 (p.7): TriLink 43.1% Resolved / 58.2% QA on Sonnet-5 and 35.6% / 64.2% on DeepSeek-v4-flash, versus best baseline 36.6% / 28.2%. FullContext reaches 58.8% but collapses to 28.2% on the weaker backbone (§5.2).[^hy-memory]
- SWE-ContextBench Lite Related (Table 3, p.8): 47.5% / 28.3% vs 45.5% / 25.3% best competing memory.[^hy-memory]
- Ablation with flash (Fig. 3, pp.7–8): removing Diff → 20.8%, Experience → 19.9%, Fact → 19.9%, from 35.6%.[^hy-memory]
- Revision strata (Fig. 4, p.9): 58/52/36 (Sonnet) and 42/41/32 (flash) at 3/4/5 revisions.[^hy-memory]
- Token efficiency (Fig. 5, p.9): 28.3% at 690 injected tokens vs MemOS 25.3% at 479 and Mem0 25.3% at 257; OpenViking/RepoMemory ~1,500 tokens at 19.2%, below NoMemory 20.2%.[^hy-memory]
- Implementation defaults in the appendix (A.3.2, Table 12, pp.18–19) match the SDK code closely: 5/5 fact/experience quotas, 0.20 thresholds, 5/3 reconcile candidates, 8 summary predecessors, 1 augmented fact with ≤3 chains, 6 lines/480 chars, 800-char said, 900-char body (Synthesis: comparison of paper and `coding/` defaults).[^hy-memory]

## Paper's own limitations (p.9 §6)

Synthetic sessions biased toward interleaving/revision; replay supplies code-object metadata for diff grouping; QA rubrics depend on LLM judgement; the three-layer links are not ablated in isolation.[^hy-memory]

## Relationships

- Evaluates: [Working and coding memory](hy-memory-working-coding-memory.md), [Diff chain](hy-memory-coding-diff-chain.md).
- Part of: [Hy Memory overview](hy-memory-overview.md).

## Coverage and limits

Only text was extracted from the PDF; figures and tables were read through their extracted text, not visually. The paper frames TriLink as three layers whereas the SDK stores two layers plus a decorator (Synthesis). Other papers in the README (EMNLP 2026, Hy-Memory-30B-A3B) are not in the repository.

[^hy-memory]: Hy-Memory monorepo, revision 9737431; PDF at `docs/papers/CMB_…pdf` (19 pages). Locators inline per claim. Evidence class Reported for paper claims; Observed for code comparisons; delegated static inspection, unexecuted.
