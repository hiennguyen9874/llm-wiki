---
type: Concept
title: RAG retrieval pipeline design
description: The decisions a retrieval pipeline makes around the embedding call — when and how to chunk, which vector store and re-embed rule to accept, how to evaluate retrieval, and where a two-stage cross-encoder reranker fits.
tags: [ml, rag, retrieval, embeddings]
status: stable
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:12:00Z }
stale_after: 2027-05-18
sources:
  - id: pydantic-embeddings-guide-2026
    resource: ../raw/guides/embeddings/index.md
    scope: ../raw/guides/embeddings/
    kind: documentation
    revision: sha256:9d0040c53252208f9c0a33843750d2fbc79dda91dbd985a19a19356582e1c3ac
    title: "Embeddings"
---

A retrieval pipeline's quality is decided by choices that interact, not by the embedding model alone: chunking, the model, the similarity metric, how many chunks are retrieved and whether a reranker runs afterwards all move the answer together[^pydantic-embeddings-guide-2026] Pydantic AI supplies only two of the parts — an [embedding call](pydantic-ai-embeddings.md) and the tool that hands retrieved text to an agent — and states explicitly that it prescribes no vector database and no chunking strategy, because those depend on the corpus, the questions and the infrastructure already in place[^pydantic-embeddings-guide-2026] The one rule it does state as a requirement rather than a preference is the re-embed rule: the index's vector dimension must match the embedder's output, and matching dimensions alone do not make vectors comparable, so changing the embedding configuration means re-embedding the documents and rebuilding or updating the index[^pydantic-embeddings-guide-2026]

## The seven steps

The documented custom pipeline is: split source documents into chunks when needed, embed the chunks with `embed_documents()`, store each vector with metadata such as source URL, title, heading, page number and permissions, embed the user's search text with `embed_query()`, search a vector index for similar chunks, optionally rerank the shortlist, and pass the retrieved text to the agent through a tool[^pydantic-embeddings-guide-2026]

Step seven is the only step Pydantic AI owns outright; step two is the `Embedder`; the rest are yours. The metadata list is the part easiest to under-build: permissions stored beside the vector are what make filtered retrieval possible later, and a chunk that cannot be traced back to its full document cannot be cited[^pydantic-embeddings-guide-2026]

## Provider-managed alternative

Before building any of it, the guide points at the opposite trade: upload or import files into a provider-managed store and pass its ID to `FileSearchTool`, after which the provider handles chunking, embeddings, storage and retrieval[^pydantic-embeddings-guide-2026] The section that follows is explicitly about the case where those choices stay application-specific — control of chunking, storage and evaluation — not about which is better, and the capture gives no comparison of quality, cost or provider coverage between the two routes[^pydantic-embeddings-guide-2026]

## Chunking

Splitting is not unconditional. The guide keeps a whole document whole unless one of three conditions holds: you want to retrieve a subsection rather than the document, the document exceeds the model's maximum input length, or the document holds enough independent facts or topics that one embedding cannot represent them precisely[^pydantic-embeddings-guide-2026]

| Strategy | Fits | Trade-off |
| --- | --- | --- |
| Document structure — headings, paragraphs, sentences, pages, records | clean, consistently structured sources | cheap and preserves natural boundaries, but uneven chunk sizes |
| Fixed-size token windows | unstructured text, strict model input limits | simple and predictable, but can split related text; overlap preserves boundary context at the cost of a larger index and duplicate hits |
| Semantic splitting | sources where topic boundaries matter more than layout | keeps related ideas together, but adds ingestion work and depends on the model and threshold |
| LLM-assisted splitting | irregular or domain-specific sources needing interpretation | most flexible, but the highest latency and cost, and the chosen boundaries need validation against source coverage |

The recommended first implementation is natural document boundaries plus a token limit, each chunk carrying source metadata and a link or identifier for the full document, evaluated before any more expensive strategy is added[^pydantic-embeddings-guide-2026] The size rule is stated as a range rather than a number: large enough to answer a focused question, small enough to avoid unrelated context, with no universally best size or strategy[^pydantic-embeddings-guide-2026]

## Vector storage

Storage is chosen on index size, query and ingestion volume, metadata filtering and permission requirements, hybrid keyword-search needs, availability requirements and existing infrastructure[^pydantic-embeddings-guide-2026] The guide's three tiers are a local index or embedded database for prototypes and small indexes (FAISS, LanceDB, SQLite with a vector extension), PostgreSQL with `pgvector` where PostgreSQL is already in use, and a managed vector or search service where hosted scaling and operational support are wanted[^pydantic-embeddings-guide-2026]

Two constraints survive any choice: dimensions must match between indexing and querying, and indexing and querying must use a compatible model configuration[^pydantic-embeddings-guide-2026] A model change is therefore a migration, not a setting — see the re-embed rule in the synthesis above.

## Evaluating retrieval, not just answers

Public benchmarks narrow the candidate list but cannot prove which complete pipeline works for a given application, because chunking, model, metric, chunk count and reranking interact[^pydantic-embeddings-guide-2026] The guide's protocol is to compare changes on queries and documents representative of production and to check both directions of the error: that relevant text is retrieved, and that irrelevant text is kept out of the agent's context[^pydantic-embeddings-guide-2026]

[Pydantic Evals](pydantic-evals.md) is named as the tool for tracking retrieval quality across a dataset of representative queries, with Hugging Face's RAG evaluation cookbook cited for building a synthetic evaluation set and grading generated answers[^pydantic-embeddings-guide-2026] The "kept out" half is the one an answer-quality score alone will not catch: an agent that answers correctly despite irrelevant context is passing an evaluation that hides a retrieval defect[^pydantic-embeddings-guide-2026] — **Synthesis**.

## Two-stage retrieval with a reranker

The two-stage pattern is a cheap broad recall pass followed by an expensive precise pass: an embedding lookup over the index produces a shortlist (the guide's example breadth is a top-100 list), and a cross-encoder then scores each candidate against the query, reading query and document together, to produce the top-5 handed to the model[^pydantic-embeddings-guide-2026] The cross-encoder is called slower and "dramatically more accurate" than an embedding lookup without a figure[^pydantic-embeddings-guide-2026]

Pydantic AI ships no reranker provider class, so the reranker is application code. The guide's local option is `CrossEncoder` from `sentence-transformers`, loaded lazily behind `functools.cache` and reused, with `CrossEncoder.rank(query, candidates, top_k=..., return_documents=True)` moved off the event loop through `asyncio.to_thread` because the call blocks[^pydantic-embeddings-guide-2026] The reranker is then called on the vector search's candidates — in the `retrieve` tool of the RAG example — before anything reaches the LLM[^pydantic-embeddings-guide-2026] Self-hosting both stages is pointed at Hugging Face Text Embeddings Inference, which serves embedding models and rerankers behind one server[^pydantic-embeddings-guide-2026]

## Limits

- The whole page rests on one vendor guide for the embedding library, not on a retrieval benchmark: it reports no recall@k, no reranker lift, no latency or cost comparison between chunking strategies, storage tiers or the provider-managed route[^pydantic-embeddings-guide-2026]
- No pipeline was built, no corpus chunked, no index created, no query run, no reranker loaded and no retrieval evaluation executed in this ingest; everything above is **Reported**, and the two **Synthesis** readings are labelled inline.
- The recommended model names (`sentence-transformers:lightonai/DenseOn`, `voyage-3.5`, `text-embedding-3-small`, the MS MARCO cross-encoder) are a snapshot, which is what the `stale_after` on this page and on [Pydantic AI embeddings](pydantic-ai-embeddings.md) dates.
- The provider-managed alternative is described in two sentences with no provider list, price, quota or retrieval-quality claim, so the choice between the two routes is left entirely to the reader[^pydantic-embeddings-guide-2026]
- The guide names no Pydantic AI version, and this page's framework-specific references (`Embedder`, `FileSearchTool`, `Pydantic Evals`) inherit that uncertainty.

## Relationships

- **Uses** [Pydantic AI embeddings](pydantic-ai-embeddings.md) for steps two and four of the pipeline and for the dimension control that the index has to match.
- **Is evaluated with** [Pydantic Evals](pydantic-evals.md), which the guide names as the place to track retrieval quality over a representative query set.
- **Competes with** the provider-managed `FileSearchTool` store, which trades control of chunking, storage and evaluation for not building any of them.
- **Depends on** metadata written at ingestion time — source, title, heading, page and permissions — which is what permission-filtered retrieval and citation later read.

[^pydantic-embeddings-guide-2026]: Pydantic Docs, "Embeddings", <https://pydantic.dev/docs/ai/guides/embeddings/>, 4,090 words as declared, no publication date and no version named; local capture `raw/guides/embeddings/index.md`, content digest sha256:9d0040c5. §"Using embeddings for RAG" (lines 98–113) for the seven-step custom pipeline, the `FileSearchTool` alternative and the metadata list; §"Chunking" (lines 114–134) for the three conditions that justify splitting, the four-strategy table, the evaluated-before-escalating advice and the size rule; §"Vector storage" (lines 135–146) for the no-prescribed-database statement, the three tiers, the dimension-match and compatibility requirement and the re-embed instruction; §"Evaluation" (lines 147–152) for the interaction of chunking/model/metric/k/reranking, the benchmark-versus-your-data argument, the two-direction check and the Pydantic Evals and cookbook pointers; §"Two-stage retrieval with rerankers" (lines 952–984) for the recall-then-rerank pattern, the top-100-to-top-5 example, the no-reranker-class statement, the `CrossEncoder`/`functools.cache`/`asyncio.to_thread` implementation and the Text Embeddings Inference pointer; §"Choosing a model" (lines 85–97) for the model-per-use-case snapshot. Evidence class: **Reported** — vendor documentation; no pipeline was built or measured.
