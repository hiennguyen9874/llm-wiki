---
type: Concept
title: txtai hybrid retrieval and ranking
description: Dense and sparse candidate generation, strategy-selected fusion, ranking surfaces, backend constraints, and model-dependent image embeddings.
tags: [rag, txtai, retrieval, ranking, multimodal]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:18:00Z }
stale_after: 2027-01-24
sources:
  - id: txtai-repo
    resource: ../raw/txtai/README.md
    scope: ../raw/txtai/
    kind: code
    revision: 738aac4
    title: txtai repository
---

**Observed:** txtai dispatches queries through graph recognition, SQL/content-backed retrieval, or plain dense/sparse indexes. When both dense ANN and sparse scoring exist, it over-fetches candidates and selects a fusion strategy from scoring-normalization flags. **Synthesis:** retrieval thresholds and score interpretations must be tied to the actual strategy/backend, not assumed interchangeable across configurations.[^txtai-repo]

## Query dispatch and candidate sizing

`Embeddings.search` wraps `batchsearch` and `Search`. Library defaults are limit **3** and weights **0.5**; the Application/service defaults differ (normally limit 10). Graph-query batches are recognized separately; content-enabled queries can use SQL, including `similar(...)`, whereas plain text goes to similarity search. Missing named subindexes raise `IndexNotFoundError`.[^txtai-repo]

Dense search transforms queries then invokes ANN; sparse search delegates to scoring. Both filter nonpositive scores. When both operate, each is asked for `limit * 10` before fusion. SQL `Scan` budgets additional candidates using limit, offset, similarity clauses, and a multi-token WHERE heuristic. SQL filtering can therefore remove candidates after search; requesting a final limit is not a guarantee of that many matching rows.[^txtai-repo]

## Hybrid fusion

| Selection order | Strategy | Observed computation |
| --- | --- | --- |
| `scoring.isbayes()` | Log-odds | Calibrate positive dense scores by median/std, transform sparse probabilities to logits, combine weighted signals, then sigmoid |
| Otherwise `isnormalized()` | Convex | Weighted sum of supplied scores |
| Otherwise | Reciprocal rank | Weighted `1/(rank + 1)`; no fixed 60 offset |

Branches with nonpositive weights are skipped. Candidates need not appear in both lists. **Synthesis:** fused probabilities, weighted scores, and reciprocal-rank sums have different meanings; a downstream RAG `minscore` should not be transferred blindly between modes. Bayesian normalization and its cited theoretical claims were observed in code/comments, not independently evaluated.[^txtai-repo]

## Sparse scoring, ranking, and explanation

Keyword indexing uses SQLite terms/postings/document statistics; BM25 defaults include `k1=1.2`, `b=0.75`. Alternatives include TF-IDF, neural sparse scoring, and Postgres full-text search. Normalization flags affect fusion. Wildcard handling, common-term candidate optimization, and tag weighting are implementation-specific, not generic Lucene equivalence.[^txtai-repo]

A separate `Reranker` pipeline wraps an embeddings search and re-scores its results with a `Similarity` pipeline; it is not automatically applied by every `Embeddings.search`. `Embeddings.explain` uses token-masking comparisons for attribution. Neither static inspection nor the presence of these APIs establishes measured ranking quality.[^txtai-repo]

## Model and ANN boundaries

ANN factories include Faiss, NumPy, HNSWlib, Annoy, torch, pgvector, sqlite-vec, Milvus, GGML, RabitQ, TurboVec, and zvec adapters; sparse ANN has its own factory. Optional imports/configuration determine availability. Backend scores, supported mutations, quantization, and native file formats differ. **Observed:** Annoy does not implement append/delete through this abstraction; RabitQ mutation support depends on its selected mode. Do not assume a backend swap preserves lifecycle operations.[^txtai-repo]

**Observed multimodal path:** transform logic can vectorize a document's `object` when text is absent. `Vectors.tokens/prepare` leave non-string/non-token-list objects unchanged; the Sentence Transformers adapter forwards them to its model's encode methods. Image encoder tests and `examples/images.py` use PIL images with CLIP-style models, while an image-search notebook also supplies an image query. This supports model-dependent image embeddings, not the claim that all images must first become captions. Actual model execution was not reproduced.[^txtai-repo]

**Limit:** sparse branches expect textual/token inputs; image-query compatibility cannot be assumed for hybrid/sparse configurations. Audio/video README claims were not traced into an equivalent model-specific execution path in this review. Precomputed arrays and custom transforms are additional extension paths, not proof of universal modality handling.[^txtai-repo]

## Documentation reconciliation

**Observed:** the general embeddings configuration documentation names `prithivida/Splade_PP_en_v2` for the sparse shortcut, while `Embeddings.defaultsparse` selects `opensearch-project/opensearch-neural-sparse-encoding-doc-v2-mini`. Use the pinned implementation for this snapshot's effective default, retaining the documentation discrepancy.[^txtai-repo]

## Relationships and limits

- **Uses:** [Persistence/SQL](txtai-persistence.md) for content joins and [graphs](txtai-graph.md) for graph-query execution.
- **Feeds:** [RAG](txtai-rag.md), whose thresholds and reference selection inherit these score semantics.
- **Used by:** [Agent tools](txtai-agents-workflows.md) and [API](txtai-api.md).
- **Part of:** [txtai architecture](txtai-architecture.md); see [coverage](txtai-source-map.md).

No retrieval recall/quality benchmark, cross-backend equivalence check, optional ANN runtime, model inference, or concurrent-write test ran. Sampled tests are implementation-intent evidence only.

[^txtai-repo]: Revision `738aac4`: `src/python/txtai/embeddings/base.py::Embeddings.search, batchsearch, defaultsparse, explain`; `embeddings/search/base.py::Search.__call__, search, dense, sparse, limit, offset, subindex`; `embeddings/search/scan.py::Scan.default`; `embeddings/search/hybrid.py::Hybrid, LogOdds`; `embeddings/search/explain.py::Explain`; `scoring/bm25.py::BM25`; `scoring/terms.py::Terms`; `scoring/factory.py::ScoringFactory`; `scoring/sparse.py::Sparse`; `scoring/pgtext.py::PGText`; `pipeline/text/reranker.py::Reranker`; `ann/dense/factory.py::ANNFactory`, `ann/base.py::ANN.append, delete`, `ann/dense/annoy.py::Annoy`, `ann/dense/rabitq.py`; `embeddings/index/transform.py::Transform.stream`; `vectors/base.py::Vectors.tokens, prepare, batchtransform, vectorize`; `vectors/dense/sbert.py::STVectors.encode`; `vectors/dense/external.py::External`; `database/encoder/image.py::ImageEncoder`; `test/python/testdatabase/testencoder.py::TestEncoder.testImages, testReindex`; `examples/images.py::Application.images`; `examples/13_Similarity_search_with_images.ipynb` image-query example; `docs/embeddings/configuration/general.md` sparse setting. Short module paths are relative to `src/python/txtai/`.
