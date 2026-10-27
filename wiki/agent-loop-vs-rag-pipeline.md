---
type: Concept
title: Agent loop versus single-shot RAG pipeline
description: A pipeline fixes what to read before reading, while an agent loop re-decides retrieval after every read, which is why technique layers stall on multi-hop questions.
tags: [rag, agentic-rag, retrieval]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T12:45:00Z }
sources:
  - id: pipeshub-frames
    resource: ../raw/agentic-rag-vs-traditional-rag-frames-benchmark/index.md
    scope: ../raw/agentic-rag-vs-traditional-rag-frames-benchmark/
    kind: article
    revision: sha256:7dc0c1387d9daf21fd3b3c7fe92fb98ba4e8b704086811eca4ffd36d9a57c51c
    title: "Agent Loop vs Traditional RAG: 92.7% vs 78.9% on FRAMES (PipesHub blog, 2026-10-01)"
---

**Synthesis:** single-shot RAG and agentic RAG differ mainly in *when* the retrieval decision is made. A fixed pipeline chooses what to read once, from the question's own words; an agent loop re-decides after every read, so each new search can be expressed with terms the previous read revealed. PipesHub's benchmark post argues that this timing, not retriever strength, explains its multi-hop result, and works one FRAMES question hop by hop to show where pipeline technique layers stall. The post is vendor-authored, so every measurement, product description, and quoted number here is **Reported**, not observed or reproduced by this wiki; the mechanism argument is **Synthesis** over the post's worked example and stated protocol.[^pipeshub-frames]

## The one decision a pipeline makes

**Reported:** a standard pipeline has two stages that each run once. It turns the question into a vector, takes the closest chunks, and pastes them into a prompt; the model then answers from exactly those chunks. "Everything the model will ever see is chosen in step 1, from the question's words alone," so the only decision the pipeline makes is *what to read* — and it makes it before reading anything.[^pipeshub-frames]

The post's worked FRAMES question asks for a future spouse's name composed from two chains: the 15th US first lady's mother, and the second assassinated president's mother's maiden name. Hops 1 and 3 are searchable from the question's wording; hops 2 and 4 need names ("Harriet Lane", "Garfield") that only the hop above them reveals, and neither name appears in the question. **Reported** outcome for that question: the pipeline's 50 chunks came from three articles, none among the five that hold the answer fragments, and the model answered "cannot be determined from the provided sources" while the same model closed-book answered from memory with the wrong first name. The post states that all 18 pipeline variants it built retrieved at most two of the five needed articles on this question and each abstained.[^pipeshub-frames]

## Why technique layers stop short

The post's technique ladder, with its own account of what each layer fixes and where it stops:[^pipeshub-frames]

| Technique | Reported mechanism | Reported stopping point |
| --- | --- | --- |
| Dense vector search | Embedding similarity over chunks | Blurs names, numbers, rare terms; can only find text that *means* something similar |
| BM25 keyword search | Rare-word-weighted term match | Needs the right words; useless when the answer article uses a name the question never states |
| Hybrid (dense + BM25, RRF merge) | Union of both ranked lists | Both searches still start from the question's words |
| Cross-encoder reranking | Score ~100 candidates against the question, keep the best 50 | Can only reorder what was retrieved, not find what was missed |
| Query expansion | Rewrite the question several ways, search each, merge | Rewriting does not reveal new names |
| Query decomposition | Split into sub-questions, search each, combine | All sub-questions are written before any search runs, so unknowable hops must be guessed |
| Small-to-big | Match small chunks, then hand the model the whole parent article | Only as good as the articles chosen; wrong top hits become whole wrong articles |
| Structure-aware chunking | Chunk on paragraphs, list items, table rows instead of fixed windows | Decides what *can* be found, not what to look for next |

**Synthesis:** the ceiling is a property of decision count, not of retriever quality. The fact that unlocks the next hop can already sit inside a retrieved document, but by the time the model reads it retrieval is closed and there is no step in which the system can say "now I know who she is, look up her mother". Decomposition comes closest because it plans several searches, yet it must plan them from the question alone, so any hop whose entity is not guessable leaves a hole that is filled from model memory rather than from retrieval.[^pipeshub-frames]

## Loop anatomy

An agent loop exposes retrieval as a *tool* the model may call repeatedly instead of handing it one fixed chunk set. Each iteration reads the accumulated state, then chooses to answer or to call a tool; the tool result is appended and the loop repeats. The decision therefore recurs after every read rather than being fixed at build time.[^pipeshub-frames]

PipesHub's stated loop also runs one search on the raw question before the first model turn, so single-pass questions can finish in one call, and it steers behavior through the system prompt rather than through new pipeline stages. The tool set is deliberately small:[^pipeshub-frames]

| Tool | Reported function |
| --- | --- |
| Search | Hybrid dense + keyword search, relevance-ranked |
| Fetch record | Read a whole document, or the next part of a long one |
| Lookup | Find a document by name or ID |
| Entities | Find people, projects and topics, and documents linked to them |
| Calculator | Exact arithmetic and date differences over values already read |

**Synthesis:** the loop is a runtime composition of the same techniques the ladder above implements as fixed stages — decomposition becomes hop-by-hop search, expansion becomes re-querying after a miss, small-to-big becomes fetching a whole record when a snippet is insufficient — but each is spent only on questions that need it. That reframing also predicts that a reranker matters less inside a loop, since the model can notice an unsatisfactory result and search again; the reported measurements for that prediction are on [retrieval technique trade-offs](rag-retrieval-technique-tradeoffs.md).

## Making a loop reliable

The post attributes most of its engineering effort not to the loop but to reliability, and reports these failure modes and fixes from reading its own failed answers on a 200-question development split (five fixes, 87.5% → 92.5% correct there):[^pipeshub-frames]

- **Long runs rarely recover.** Answers taking one to six model calls were 90–94% correct; those taking thirteen or more were almost never right. Raising the turn limit added cost without adding accuracy; the post's recommendation is to make each tool result more useful so fewer turns are needed.
- **Reading budgets must be shared.** With several documents requested at once, the first consumed the whole budget and later documents returned empty 72 times across 200 questions; splitting the budget fairly fixed it at no extra cost.
- **The provider's safety filter is part of the system.** A "please wrap up" note sent as a system-style message after a tool result was blocked every time the run was replayed, showing the user a canned refusal; the same words attached to the tool result passed every time. Ordinary factual questions were also refused because of text the system had retrieved, which the post recommends treating as its own error type.
- **Exact tools for exact work.** Date and arithmetic errors stopped once a calculator was reachable from the first turn.
- **Remove what the task does not need.** A search mode that dropped file generation, image generation, code execution and web search cut the system prompt from about 4,600 to about 3,200 tokens and the tool list from 35 to 14.
- **Parsing decides what can be found.** Tables whose row labels were parsed as headers lost their data, and link URLs made up a third of the text embedded in one stage; the post claims parsing fixes helped more questions than any retrieval tweak.

## Relationships

- **Contrasted by measurement:** [PipesHub's self-reported FRAMES benchmark](frames-agentic-rag-benchmark.md) quantifies pipeline-versus-loop accuracy, cost and latency under one protocol.
- **Uses:** hybrid retrieval as its search tool — implemented in [OpenRAG](openrag-hybrid-retrieval.md), [RAGFlow](ragflow-retrieval.md), [WeKnora](weknora-hybrid-retrieval.md), [LightRAG](lightrag-retrieval.md), and [txtai](txtai-retrieval.md).
- **Comparable mechanism:** [WeKnora agent turn runtime](weknora-agent-runtime.md) and [RAGFlow agent workflows](ragflow-agent-workflows.md) are code-grounded ReAct/canvas loops whose budgets, tools and steering are inspectable in source; this page describes a vendor's loop only through prose and a linked, uninspected repository.
- **Measured by:** [grounded-accuracy evaluation](grounded-accuracy-evaluation.md) supplies the control conditions needed to compare the two architectures honestly.

## Evidence and limits

- **Reported only, vendor-authored.** The post is PipesHub's own product argument for its own platform. Per this instance's scope rules such claims are carried as claims and never as measured capability; no number on this page was produced, reproduced, or independently audited here.
- **No repository inspected.** The loop, tools and prompts are said to be readable in `github.com/pipeshub-ai/pipeshub-ai`, but that repository is not in `raw/`, so implementation described here is the post's description, not observed source.
- **Single worked example.** The hand-traced question is one deliberately chosen illustration, not a sample; per-technique article-coverage figures for it are anecdotal until matched against the full 18-variant board.
- **Coverage of this source.** The capture is one 508-line HTML-to-Markdown article (`raw/agentic-rag-vs-traditional-rag-frames-benchmark/index.md`, read in full). Seven embedded `framerusercontent.com` video elements were not transcribed, so any content unique to them is uncovered. Linked external evidence — the PipesHub repository and its `integration-tests/benchmarks/REPRODUCE.md`, the arXiv FRAMES paper (2409.12941), and the Google Research agentic-RAG post — was not fetched and is recorded as unavailable here, not as corroboration.

[^pipeshub-frames]: PipesHub blog post "Agent Loop vs Traditional RAG: 92.7% vs 78.9% on FRAMES", `raw/agentic-rag-vs-traditional-rag-frames-benchmark/index.md` (local capture 2026-10-26, sha256 `7dc0c138…57c51c`, published 2026-10-01): frontmatter (`site`, `published`, `word_count: 8118`); headings and paragraphs "A multi-hop question, worked through by hand"; "How a traditional RAG pipeline works" ("Everything the model will ever see is chosen in step 1"); "RAG techniques compared: hybrid search, reranking, query expansion, decomposition and small-to-big" (items 1–8); "Why every RAG technique hits the same ceiling"; "Agentic RAG: how an agent loop works" and its "The multi-hop question, turn by turn" walkthrough; "How PipesHub builds an agent loop for enterprise search" (three-layer description, tools table, reliability bullets); "Lessons for teams building RAG and AI agents" subsections "Building the loop" and "Preparing the data". Single-artifact capture, no revision beyond the local digest, no linked artifact inspected.
