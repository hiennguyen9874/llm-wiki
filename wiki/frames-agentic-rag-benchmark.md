---
type: Concept
title: FRAMES agent-loop benchmark (PipesHub, self-reported)
description: A vendor-published 824-question FRAMES comparison reports 92.7% for an agent loop against 78.9% for its best of 18 RAG pipelines, with stated protocol, costs, and unresolved confounds.
tags: [rag, benchmark, evaluation, agentic-rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T12:50:00Z }
stale_after: 2027-04-26
sources:
  - id: pipeshub-frames
    resource: ../raw/agentic-rag-vs-traditional-rag-frames-benchmark/index.md
    scope: ../raw/agentic-rag-vs-traditional-rag-frames-benchmark/
    kind: article
    revision: sha256:7dc0c1387d9daf21fd3b3c7fe92fb98ba4e8b704086811eca4ffd36d9a57c51c
    title: "Agent Loop vs Traditional RAG: 92.7% vs 78.9% on FRAMES (PipesHub blog, 2026-10-01)"
---

**Reported, vendor-authored:** PipesHub publishes a comparison of its agent loop against 18 RAG pipeline variants it built on Google's 824-question FRAMES multi-hop benchmark, reporting 92.7% accuracy (95% CI 90.9–94.4) and 84.0% grounded accuracy for its own system, against 78.9% / 73.2% for its best pipeline and 93.0% / 90.0% for an oracle handed the exact source articles. **Synthesis:** the result is the most explicit public instance in this wiki of the decision-timing argument in [agent loop versus single-shot RAG pipeline](agent-loop-vs-rag-pipeline.md), but it is a self-reported product benchmark whose headline row compares a full product against bare pipelines, so it supports "this difference can be large" rather than "this system is 13.8 points better than agentic RAG in general".[^pipeshub-frames]

## Stated protocol

Conditions the post says were held fixed across every row:[^pipeshub-frames]

- One answering model for all systems (`gpt-5.6-luna`, high reasoning effort) and one embedding model (`text-embedding-3-small`).
- One corpus: 12,441 Wikipedia articles frozen at their 15 October 2024 versions — the 2,517 articles the questions need plus roughly 10,000 linked distractors.
- One price table, with every model call counted, including rewrite and decomposition calls a pipeline makes.
- Two controls: *closed book* (no documents, measures answerable-from-memory) and *oracle* (the exact needed articles supplied, measures the model's ceiling).
- Grounding enforced by both instruction and check: every system was told to answer only from retrieved text and to say what is missing, then every correct answer was checked against the exact text the system was shown; a correct answer whose facts were not in that text is flagged *memory-suspect*.
- Two independent graders, Claude Sonnet 5 with the FRAMES paper's grading prompt verbatim and Gemini 3.8 Flash.
- A 200-question development / 624-question held-out split, stratified by reasoning type; reported fixes were developed on dev only, and both the full 824 and the held-out 624 are reported.
- Every system answered every question: failed calls were retried, and 38 pipeline answers refused by Azure's content filter for their retrieved text were re-asked through the same model on OpenAI's endpoint, which refused none.

## Reported results, all 824 questions

| System | Accuracy | Grounded accuracy | Latency median / p95 | Mean cost per question | Mean cost per correct answer |
| --- | ---: | ---: | --- | ---: | ---: |
| Closed book (memory only) | 64.9% | — | 7 s / 95 s | $0.0030 | $0.0047 |
| Naive RAG (dense, top 50) | 36.3% | 27.7% | 7 s / 18 s | $0.0014 | $0.0039 |
| Hybrid search | 43.3% | 36.8% | 8 s / 18 s | $0.0018 | $0.0040 |
| Hybrid + reranker | 46.2% | 39.7% | 9 s / 21 s | $0.0019 | $0.0040 |
| Hybrid + query expansion | 73.4% | 67.5% | 17 s / 25 s | $0.0019 | $0.0026 |
| Hybrid + expansion + reranker | 64.7% | 56.8% | 33 s / 109 s | $0.0020 | $0.0030 |
| Hybrid + expansion + small-to-big (best pipeline) | 78.9% | 73.2% | 27 s / 54 s | $0.0056 | $0.0071 |
| PipesHub agent loop | 92.7% | 84.0% | 22 s / 134 s | $0.0167 | $0.0180 |
| Oracle (exact articles given) | 93.0% | 90.0% | 3 s / 6 s | $0.0049 | $0.0053 |

Held-out subset (624 questions, never used for tuning): agent loop 92.3% / 84.5% grounded, best pipeline 78.7% / 73.2%. Under a stricter grader that rejects hedged or multi-candidate answers, the agent loop scores 91.6% and the best pipeline 78.0%.[^pipeshub-frames]

**Synthesis:** two rows matter beyond the headline. Naive dense RAG (36.3%) scored far *below* closed-book memory (64.9%) on this benchmark, so retrieval that surfaces the wrong passages can be worse than no retrieval; and the entire pipeline ladder except small-to-big sits far below the memory baseline, which is a warning that these FRAMES questions reward recall of the right linking fact more than plausible surrounding text.

## Where the gap grows

- **Hops.** On questions built from two gold articles the best pipeline reached 87% and the loop 93%; on five or more articles the pipeline fell to 62% while the loop held 90%.[^pipeshub-frames]
- **Article coverage.** The loop's model saw every gold article on 84% of questions, the best pipeline's on 75%. When an article was missing, the loop still produced grounded answers 76% of the time against 34% for the pipeline, which the post attributes to recovering the same facts from list pages and related articles.[^pipeshub-frames]
- **Against the oracle.** The loop matched oracle accuracy but stayed about five points behind on grounded accuracy, each being right on roughly 30 questions the other missed.[^pipeshub-frames]
- **Memory drift.** With the added instruction "Do not answer questions from your training memory", 6 of the loop's correct answers (0.8%) filled a linking fact from memory, the same rate as the best pipeline (5, 0.8%); the oracle did so twice. Without the instruction the loop drifted in 13 answers (1.7%) at the same 92.7% accuracy — so a one-line instruction halved the behavior without changing measured accuracy.[^pipeshub-frames]

## Cost and latency shape

| Model calls used by the loop | Share of questions | Median time | Median cost | Correct |
| --- | ---: | --- | ---: | ---: |
| 1 | 21% | 8 s | $0.0062 | 95% |
| 2 | 43% | 19 s | $0.0101 | 95% |
| 3 | 20% | 32 s | $0.0136 | 95% |
| 4 | 8% | 47 s | $0.0216 | 91% |
| 5 or more | 7% | 134 s | $0.0604 | 70% |
| Best pipeline (every question) | 100% | 27 s | $0.0053 | 79% |
| Naive RAG (every question) | 100% | 7 s | $0.0011 | 36% |

**Reported:** one-pass questions cost about the same as the strongest pipeline and return roughly three times faster (8 s vs 27 s); the 7% of questions needing five or more calls consumed 37% of total spend and were the least accurate. Mean cost per question ($0.0167) exceeded median ($0.0105) by about 60%, and 47% of the loop's input tokens were served from provider prompt cache, against none for the pipelines.[^pipeshub-frames]

**Synthesis:** the economically decisive comparison on this board is cost per *correct* answer, where hybrid + query expansion ($0.0026) beats the agent loop ($0.0180) by roughly 7× and the best pipeline ($0.0071) by roughly 2.7×. The loop's advantage is accuracy on five-article questions, not efficiency; any adoption argument should state which side of that trade-off the workload sits on.

## Confounds and comparability limits

- **Whole product versus bare pipelines (author-disclosed).** Each pipeline got a short answer prompt of about 150 words and no tools; PipesHub got its search-mode prompt with tool definitions, citation rules and multi-step rules at about 7,400 input tokens on its first call, plus search, fetch-record and calculator tools. The post states plainly that its row "measures the whole product against the pipelines, not the loop alone" and that prompt and turns explain most of its cost. **Synthesis:** the comparison therefore does not isolate loop-versus-pipeline architecture; a pipeline given equally capable tools and an equally long prompt remains untested here.[^pipeshub-frames]
- **Single dataset, corpus, and model.** One synthetic-document benchmark, one Wikipedia corpus frozen at 2024-10-15, one answering model. No variance across models, no enterprise/document-corpora replication.
- **Latency caveat (author-disclosed).** Timings came from one laptop that was running other benchmark jobs concurrently, described as a comparison rather than production latency.
- **Grading.** Two judges are named and their use is described, but the capture contains no inter-judge agreement figure despite promising one, and the full board with all 18 variants and confidence intervals lives in the repository rather than in the post.[^pipeshub-frames]
- **Reproduction unverified.** The post claims everything is pinned by hash and re-runnable on one machine from `integration-tests/benchmarks/REPRODUCE.md`. Neither the repository nor that runbook is present in `raw/`, nothing was executed here, and no independent rerun of FRAMES by a third party for this system was found in the capture.
- **Adjacent reported results are not comparable rows.** The FRAMES paper's own baselines (0.40 closed-book, 0.66 for a multi-step retrieval pipeline) and Google Research's 90.1% agentic-RAG figure are cited by the post with different models, corpora and unpublished judges; they are directionally consistent, not corroboration of the table above.[^pipeshub-frames]

## Relationships

- **Supersedes no prior concept; depends on** [agent loop versus single-shot RAG pipeline](agent-loop-vs-rag-pipeline.md) for the mechanism it measures.
- **Uses** the evaluation controls documented in [grounded-accuracy evaluation](grounded-accuracy-evaluation.md).
- **Quantifies** the technique ranking described in [retrieval technique trade-offs](rag-retrieval-technique-tradeoffs.md); the two pages report the same runs and should be updated together.
- **Comparable in intent, not method:** [UltraRAG benchmarking and evaluation](ultrarag-evaluation.md), [RAG-Anything reproduction and evaluation](rag-anything-reproduction-evaluation.md), and [Ragas retrieval and answer-quality metrics](ragas-rag-metrics.md) concern code-grounded or framework-level evaluation rather than a vendor-run benchmark.

## Evidence and limits

`draft`, because the page records a vendor's claims about its own system: every figure is **Reported** and none is **Observed** or **Reproduced** in this wiki. It is useful for one retrieval purpose — conditioning expectations for agentic-versus-pipeline multi-hop performance, cost, and latency. Treat the model names, prices, and versioned figures as time-sensitive (`stale_after` set accordingly) and re-check them against a pinned rerun before quoting them as capability. Coverage: the single captured article was read in full; its seven embedded videos, the linked repository, `REPRODUCE.md`, the FRAMES paper, and the Google Research post were not inspected.

[^pipeshub-frames]: PipesHub blog post "Agent Loop vs Traditional RAG: 92.7% vs 78.9% on FRAMES", `raw/agentic-rag-vs-traditional-rag-frames-benchmark/index.md` (local capture 2026-10-26, sha256 `7dc0c138…57c51c`, published 2026-10-01, `word_count: 8118`): headings "TL;DR: executive summary", "Key findings", "How we benchmarked RAG on FRAMES" (subsections "The same inputs for everyone", "Two reference points", "Grading", "Splits"), "FRAMES benchmark results: agent loop vs RAG pipelines" (results table and footnotes: grounded-accuracy definition, laptop latency caveat, 38 Azure-filtered pipeline answers), "What the numbers show" (hop split, gold-article coverage, memory-drift counts, strict-grader result), "Cost and latency of agentic RAG" (per-call table, prompt-cache share, complexity), "Other published results on FRAMES", plus the comparison table "Agent loop vs RAG pipeline". Single-artifact capture, local digest as revision, no linked artifact inspected.
