---
type: Concept
title: Retrieval technique trade-offs on multi-hop questions
description: On one reported FRAMES board, query expansion and small-to-big raise pipeline accuracy while a weak cross-encoder reranker lowers a good pipeline by nearly nine points.
tags: [rag, retrieval, ranking, benchmark]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T12:55:00Z }
stale_after: 2027-04-26
sources:
  - id: pipeshub-frames
    resource: ../raw/agentic-rag-vs-traditional-rag-frames-benchmark/index.md
    scope: ../raw/agentic-rag-vs-traditional-rag-frames-benchmark/
    kind: article
    revision: sha256:7dc0c1387d9daf21fd3b3c7fe92fb98ba4e8b704086811eca4ffd36d9a57c51c
    title: "Agent Loop vs Traditional RAG: 92.7% vs 78.9% on FRAMES (PipesHub blog, 2026-10-01)"
---

**Reported:** on a single 824-question FRAMES board, the two pipeline changes that moved accuracy most were query expansion (hybrid 43.3% → 73.4%) and small-to-big over expanded queries (73.4% → 78.9%), while adding a 22M-parameter cross-encoder reranker to the expansion pipeline *reduced* accuracy from 73.4% to 64.7%. **Synthesis:** these deltas are consistent with one mechanism — each pipeline stage works on the fixed candidate pool chosen from the original question, so a stage that re-scores candidates against that same question can discard the passage a rephrased query had correctly found. All figures come from a vendor's self-reported benchmark and are **Reported** here, not reproduced; their protocol and confounds are on [PipesHub's FRAMES benchmark](frames-agentic-rag-benchmark.md).[^pipeshub-frames]

## Reported pipeline ladder

| Pipeline | Accuracy | Grounded accuracy |
| --- | ---: | ---: |
| Naive dense (top 50) | 36.3% | 27.7% |
| Hybrid (dense + BM25) | 43.3% | 36.8% |
| Hybrid + decomposition | 57.8% | — |
| Hybrid + query expansion | 73.4% | 67.5% |
| Hybrid + query expansion + small-to-big (best) | 78.9% | 73.2% |
| Hybrid + expansion + small reranker | 64.7% | 56.8% |
| Hybrid + expansion + strong reranker | 74.8% | — |
| Hybrid + decomposition + small reranker | 55.1% | — |
| Hybrid + decomposition + strong reranker | 75.5% | — |

**Synthesis:** the ladder's shape matters more than any single cell. Query expansion is the largest single pipeline gain in the board (+30.1 points over hybrid), small-to-big adds a further +5.5, and reranking is the only stage that is reported to *lose* accuracy in one configuration. A platform that ships hybrid search plus a reranker as its default — as several compiled systems do — would land in the 43–46% region of this board, not near it.[^pipeshub-frames]

## Small-to-big: read the whole article, not a better list

**Reported:** small-to-big searches over small chunks, then hands the model the full articles those chunks came from. Added to hybrid + expansion it raised accuracy from 73.4% to 78.9% (79 questions gained, 33 lost), roughly tripled the mean cost per question ($0.0019 → $0.0056) and added about ten seconds.[^pipeshub-frames]

The post's own explanation is that it found no more of the correct articles; the gain came from reading the whole of articles already found, because the linking fact of a multi-hop answer often sits outside the retrieved chunk window. **Synthesis:** this is an evidence-breadth fix, not a ranking fix — it works when the missing fact is adjacent to a correct hit, and cannot help when the top hits come from the wrong article, which is the dominant failure mode in the same benchmark for the harder questions.

PipesHub's `Fetch record` tool is presented as the same job done under model control: the loop chooses which records to read instead of always reading the top few.[^pipeshub-frames]

## Reranker behavior: weak hurts, strong recovers

- **Weak reranker on a good pipeline.** The shipped small cross-encoder (`ms-marco-MiniLM-L-6-v2`, 22M parameters) scored the top 100 candidates and kept 50. It helped plain hybrid search slightly (43.3% → 46.2%, +2.9) but cost hybrid + expansion 8.7 points (73.4% → 64.7%; 122 questions lost, 50 gained) and cost decomposition 2.7 points (57.8% → 55.1%).[^pipeshub-frames]
- **Reported mechanism.** The same articles were retrieved; what changed was which passages reached the model. The reranker scores every candidate against the *original* question, and a passage holding a linking fact rarely resembles that question, so a passage found by a rephrased query was dropped. The model then abstained far more often: 241 "I don't know" answers against 161 without the reranker.[^pipeshub-frames]
- **Strong reranker on the expansion pipeline.** A 568M-parameter model (`BAAI/bge-reranker-v2-m3`) lifted expansion + reranking to 74.8%, recovering the loss, and decomposition + reranking to 75.5%. The post characterizes the remaining gain over the unexpanded pipeline as statistically insignificant (67 questions gained, 50 lost) and as an expensive point: about two minutes per question on the authors' laptop GPU, implying GPU serving in production.[^pipeshub-frames]
- **Guidance the post offers.** Measure a reranker on your own multi-hop questions, prefer a strong model, and consider scoring candidates against each expanded query rather than only against the original question. It also argues an agent loop needs a reranker least, because the loop can judge what it read and search again instead of re-sorting a fixed pool.[^pipeshub-frames]

**Synthesis:** the result is best read as a warning about stage composition rather than about cross-encoders in general. When one stage broadens the candidate set via query rewriting, a later stage that re-imposes fidelity to the original question can undo it; evaluation that adds each stage in isolation would never reveal this interaction.

## Reported inconsistency to keep open

The post states the strong 568M reranker scored 75.5%, "about eleven points above the small one and 2.1 points above no reranker". Those comparisons are not on the same pipeline: 75.5% is the decomposition row, whose own no-reranker value is 57.8% (+17.7, not +2.1), while the expansion row's strong-reranker value is 74.8% (+1.4 over 73.4%). **Synthesis:** the "2.1 points" figure appears to compare the strong reranker on decomposition against no reranker on expansion. This wiki records both readings rather than choosing one; a pinned rerun of the board would settle it.[^pipeshub-frames]

## Relationships

- **Contrasts with:** [agent loop versus single-shot RAG pipeline](agent-loop-vs-rag-pipeline.md), which argues these stages are better spent on demand inside a loop.
- **Measures the same runs as:** [PipesHub's FRAMES benchmark](frames-agentic-rag-benchmark.md); update both pages together.
- **Compares with implementation-level retrieval concepts:** [RAGFlow hybrid retrieval and ranking](ragflow-retrieval.md) (parent-child promotion), [WeKnora hybrid retrieval and reranking](weknora-hybrid-retrieval.md) (RRF normalization, rerank degradation, MMR), [LightRAG retrieval modes and ranking](lightrag-retrieval.md), [OpenRAG hybrid retrieval](openrag-hybrid-retrieval.md), [txtai hybrid retrieval](txtai-retrieval.md), and [UltraRAG retrieval and reranking](ultrarag-retrieval.md) — those pages describe how each platform composes rankers, this page reports one measurement of what composition costs.
- **Uses** the controls in [grounded-accuracy evaluation](grounded-accuracy-evaluation.md) to separate "correct" from "correct from retrieved text".

## Evidence and limits

`draft`, because every delta is a vendor's self-report from one board, one answering model and one corpus, with no confidence intervals for the pipeline rows in the capture and no independent rerun. It is useful for one retrieval purpose — deciding whether to add query expansion, small-to-big, or a reranker to a multi-hop RAG pipeline, and what interaction risk to test when composing them. Reranker model names, parameter counts and throughput figures are time-sensitive (`stale_after` set). Coverage: the single article was read in full; the repository's full 18-variant board, its confidence intervals, and the reranker serving benchmarks were not inspected, and nothing was executed.

[^pipeshub-frames]: PipesHub blog post "Agent Loop vs Traditional RAG: 92.7% vs 78.9% on FRAMES", `raw/agentic-rag-vs-traditional-rag-frames-benchmark/index.md` (local capture 2026-10-26, sha256 `7dc0c138…57c51c`, published 2026-10-01): headings "RAG techniques compared: hybrid search, reranking, query expansion, decomposition and small-to-big" (items 4, 5, 6, 7 and their "On all 824 questions" notes), "FRAMES benchmark results: agent loop vs RAG pipelines" (results table), "What the numbers show" (strict grader, gold-article coverage), "Reranker insights: when a cross-encoder reranker helps and when it hurts" (reranker table and the three bullets including the 2.1-point claim), "How PipesHub builds an agent loop for enterprise search" (`Fetch record` tool), and "Why an agent loop beats a RAG pipeline on multi-hop questions". Single-artifact capture, local digest as revision, no linked artifact inspected.
