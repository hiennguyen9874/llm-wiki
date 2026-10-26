---
type: Concept
title: Grounded-accuracy evaluation for RAG and agent answers
description: Closed-book and oracle controls, grounding checks against what a system actually read, and trace-fidelity pitfalls separate retrieval success from parametric recall.
tags: [rag, evaluation, benchmark]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T13:00:00Z }
sources:
  - id: pipeshub-frames
    resource: ../raw/agentic-rag-vs-traditional-rag-frames-benchmark/index.md
    scope: ../raw/agentic-rag-vs-traditional-rag-frames-benchmark/
    kind: article
    revision: sha256:7dc0c1387d9daf21fd3b3c7fe92fb98ba4e8b704086811eca4ffd36d9a57c51c
    title: "Agent Loop vs Traditional RAG: 92.7% vs 78.9% on FRAMES (PipesHub blog, 2026-10-01)"
---

**Synthesis:** an accuracy figure for a RAG system is uninterpretable without three things: a *closed-book* control showing how much the chosen model already knows, an *oracle* control showing the model's ceiling when given the exact evidence, and a *grounding check* that verifies each correct answer's facts appeared in the text that system actually read. PipesHub's benchmark post converts this argument into a working protocol — including its own debugging failures — which is more transferable than its product numbers. The protocol below is **Synthesis** of the post's described practice; the quoted measurements are **Reported** vendor results from that one benchmark, not reproduced here.[^pipeshub-frames]

## Why accuracy alone is ambiguous

**Reported:** on the 824 FRAMES questions, the same answering model scored 64.9% with no documents at all, while naive dense RAG scored 36.3% and plain hybrid 43.3%. The agent loop scored 92.7% but only 84.0% *grounded*, and an oracle handed the exact needed articles scored 93.0% with 90.0% grounded.[^pipeshub-frames]

**Synthesis:** three distinct things are being measured in those numbers — what the model remembers, what retrieval added, and whether the composed system stayed anchored to evidence. A single accuracy column conflates them, and in this board the memory baseline alone exceeded every pipeline except the two best, so a "retrieval improvement" can be an illusion produced by the base model. The post's own example shows the opposite failure too: the pipeline correctly answered "cannot be determined from the provided sources" while the closed-book model produced a confident wrong name, trading a wrong answer for no answer.

## The control set

- **Closed book.** Answer with no documents, same model and prompt shape. Establishes the memory floor and therefore how much credit retrieval deserves.[^pipeshub-frames]
- **Oracle.** Supply the exact gold articles for each question. Establishes the ceiling for this model and grader, which lets a score be read as a fraction of what is achievable rather than as an absolute. The post reports the loop matching oracle accuracy but trailing about five points on grounding.[^pipeshub-frames]
- **Grounded accuracy.** A correct answer counts as grounded only if the key facts appeared in the text that system was shown; the post's definition is applied at grading time, not by trusting the system's citations.[^pipeshub-frames]

## Ask for grounding, then check that you got it

**Reported:** every system was instructed to answer only from retrieved text and to state what was missing, and PipesHub additionally ran with the custom instruction "Do not answer questions from your training memory". Even so, the loop filled one linking fact from memory in 13 of its correct answers (1.7%) without the instruction and 6 (0.8%) with it, at identical 92.7% accuracy; the best pipeline did so 5 times (0.8%) and the oracle twice. The post's conclusion is that a prompt reduces memory drift while only a grading-time check measures what remains, and that citations prove where *some* of an answer came from, not all of it — each drifting answer cited sources for its other facts.[^pipeshub-frames]

**Synthesis:** the practical rule is that "answer only from context" instructions are cheap and should be used, but a benchmark that records only accuracy will systematically reward a system whose retriever fails while its model fills the gap from memory. That is precisely the regime where a RAG deployment is unsafe and where its benchmark looks fine.

## Trace and checker fidelity

Two of the post's most reusable findings are about the measurement apparatus rather than the systems being measured:[^pipeshub-frames]

- **Incomplete traces bias grounding downward.** Twice the harness's own trace omitted text the system had shown its model — the rows of a table after the first match, and the rows of a table read in full — making correct answers look memory-derived. Fixing trace completeness moved reported grounded accuracy from 69% to 84% while accuracy stayed at 93%.
- **A truncating checker cuts exactly the evidence multi-hop answers need.** The grounding checker originally read at most 6,000 tokens of evidence, keeping passages that looked most similar to the question. Linking facts rarely resemble the question, so they were cut first, and the oracle appeared to have answered 55 questions from memory; re-checking the full evidence brought that to 2.

**Synthesis:** both failures are silent and one-directional. A trace gap understates grounding, a truncating checker understates it further, and neither is visible in the headline accuracy. Any grounding claim therefore needs an audit of what the trace recorded and what the checker was allowed to read — and the oracle control is what exposes such bias, because a system given every needed article should not appear to answer from memory.

## Grading, splits, and reporting hygiene

- **Two independent judges** score each answer — here Claude Sonnet 5 with the FRAMES paper's grading prompt verbatim, plus Gemini 3.8 Flash — and the post reports robustness by re-scoring under a stricter grader that rejects hedged or multi-candidate answers, where the loop scores 91.6% and the best pipeline 78.0%.[^pipeshub-frames]
- **Held-out split.** 200 development and 624 held-out questions, stratified by reasoning type; all tuning happened on dev, and the full-set and held-out numbers are reported separately (92.7% vs 92.3% for the loop). This is what makes the result resistant to the charge that it was tuned on the test set.[^pipeshub-frames]
- **Cost accounting.** Every model call is counted, including rewrite and decomposition calls the pipeline makes; cost is reported as mean per question *and* mean per correct answer. Reporting only latency medians hides the expensive tail: the loop's median was 22 s but its p95 was 134 s, and 7% of questions consumed 37% of spend.[^pipeshub-frames]
- **Read the traces.** The post attributes most of its debugging progress to inspecting which blocks reached the model, which surfaced budget, table-parsing and filter problems in minutes.[^pipeshub-frames]

## Contradiction to keep open

The post promises to report how often its two graders agree but the capture contains no agreement figure, so judge reliability is asserted by design rather than by measurement here. It also reports that the added memory instruction left accuracy unchanged at 92.7% while halving memory drift, which means the two runs it compares are not the same run and the accuracy equality should be read as coincidence-compatible, not as a controlled invariance.[^pipeshub-frames]

## Relationships

- **Applied by:** [PipesHub's FRAMES benchmark](frames-agentic-rag-benchmark.md) and the pipeline deltas on [retrieval technique trade-offs](rag-retrieval-technique-tradeoffs.md).
- **Contrasts with:** [agent loop versus single-shot RAG pipeline](agent-loop-vs-rag-pipeline.md), which is a mechanism argument that this protocol is designed to test rather than an evaluation method itself.
- **Related evaluation concepts:** [Ragas retrieval and answer-quality metrics](ragas-rag-metrics.md) supplies framework-level metrics such as context support and ranked precision; [UltraRAG benchmarking and evaluation](ultrarag-evaluation.md) and [RAG-Anything reproduction and evaluation](rag-anything-reproduction-evaluation.md) show how hard reproducible evaluation is in code-grounded repositories. None of them implements a grounded-accuracy control of this shape.

## Evidence and limits

`stable` as a procedure: the protocol and its failure modes are stated completely, and the page's judgement about trace and checker bias is **Synthesis** over the post's own reported debugging record rather than a measurement this wiki performed. Its numbers remain **Reported** vendor results and are not evidence of capability. Coverage: the single captured article was read in full; the benchmark repository, harness code, grading prompts and the FRAMES paper were not inspected, so implementation-level details of the checker (for example how "key facts" are matched) are unknown here.

[^pipeshub-frames]: PipesHub blog post "Agent Loop vs Traditional RAG: 92.7% vs 78.9% on FRAMES", `raw/agentic-rag-vs-traditional-rag-frames-benchmark/index.md` (local capture 2026-10-26, sha256 `7dc0c138…57c51c`, published 2026-10-01): headings "How we benchmarked RAG on FRAMES" and its subsections "Two reference points", "Answers must come from the documents", "Grading", "Splits"; "FRAMES benchmark results: agent loop vs RAG pipelines" (grounded-accuracy definition and laptop latency footnote); "What the numbers show" (memory-drift counts, strict-grader result); "Cost and latency of agentic RAG" (tail and mean-versus-median paragraphs); "Lessons for teams building RAG and AI agents" subsection "Measuring it" (trace-gap and truncating-checker bullets). Single-artifact capture, local digest as revision, no linked artifact inspected.
