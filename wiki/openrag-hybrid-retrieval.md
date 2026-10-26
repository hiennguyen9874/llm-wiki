---
type: Concept
title: "OpenRAG hybrid retrieval and embedding spaces"
description: "Parallel backend and Langflow hybrid search, embedding-space routing, DLS-aware thresholds, and keyword fallback behavior."
tags: [ml, openrag, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:56:21Z }
stale_after: 2027-01-24
sources:
  - id: openrag-repo
    resource: ../raw/openrag/README.md
    scope: ../raw/openrag/
    kind: code
    revision: 6fc819d
    title: OpenRAG repository
---

**Observed:** OpenRAG implements hybrid retrieval in both the backend `SearchService` and a Langflow OpenSearch component. Both combine per-model vector clauses with keyword matching, but their query details differ; one must not assume the search UI and an agent tool generate identical requests or rankings.[^openrag-repo]

## Ranking and filtering

| Feature | Backend | Langflow component |
| --- | --- | --- |
| Vector mixture | `dis_max`, tie breaker 0, boost 0.7 | Same mixture pattern |
| Keyword mixture | `multi_match` boost 0.3 with vectors, 1.0 without | Same broad weighting |
| Text fields | `text^2`, `filename^1.5` | Same fields |
| Extra backend clause | `match_phrase_prefix`, boost 0.25, max expansions 50 | Not the same inspected query composition |
| Fuzziness | `AUTO:4,7` | `AUTO` |

These are query boosts, **not normalized probabilities or a guaranteed 70/30 contribution to final scores**. Backend vector search uses `k=50`, `num_candidates=1000`; request result limit defaults to 10. Facets include data sources, document types, owners, and embedding models.[^openrag-repo]

A key security/search interaction: the backend applies score filtering inside `function_score` with `min_score`, rather than a naive top-level threshold. The code explains that OpenSearch DLS adds a constant-score clause that could otherwise lift all visible documents over the cutoff. This rationale is observed in code, not independently benchmarked.[^openrag-repo]

## Multiple embedding spaces

Documents carry embedding model/provider/dimension and space identity. Vector fields are model-qualified; discovery distinguishes qualified spaces from legacy entries. The embedding component routes `space:<space_id>` and `legacy:` identifiers. Existing documents without `embedding_space_id` remain keyword-discoverable rather than being blindly compared across incompatible embeddings.[^openrag-repo]

**Observed degradation:** no usable embedding spaces → keyword-only search; vector-field errors can trigger a keyword retry; unsupported `num_candidates` can trigger a retry without that option. **Reported:** querying several embedding models costs additional searches and unavailable old models can cause failed or incomplete chat results. Changing the active ingest model is not retroactive re-embedding.[^openrag-repo]

## Retrieval-to-agent trust contract

`fence_untrusted_text` wraps retrieved content in explicit untrusted-document delimiters and escapes existing delimiters first, so a chunk cannot trivially forge its closing marker. The agent prompt tells the model that document text is data, not instructions. **Unverified:** this is a defense mechanism, not proof of prompt-injection resistance.[^openrag-repo]

Knowledge filters constrain subsets by query, data source, document type, owner, and connector. A convenience filter is not a substitute for DLS or RBAC. The documented default filter response limit is 10 and threshold 0.[^openrag-repo]

## Relationships

- Depends on [ingestion](openrag-document-ingestion.md) for embedding-space and ACL metadata.
- Uses [authentication/security](openrag-auth-security.md) for DLS and [chat prompts](openrag-chat-streaming.md) for untrusted-text handling.
- Exposed through the [public API](openrag-public-api.md) and [Langflow workflows](openrag-langflow-workflows.md).

## Coverage limits

No ranking-quality, recall, vector compatibility, DLS threshold, or fallback tests were run. Provider routing and the full embedding-space test suite remain partly pending; see [source map](openrag-source-map.md).

[^openrag-repo]: `6fc819d`: `src/services/search_service.py::{_search}` and embedding-space discovery (approximately lines 404–460, 596–700); `custom_components/openrag/opensearch_multimodal.py::{search,fence_untrusted_text}` and embedding-field construction; `custom_components/openrag/openai_compatible_embedding.py` routing contract; `src/api/search.py`; `src/auth_context.py`; `flows/openrag_agent.json` prompt/filter wiring; `docs/docs/core-components/ingestion-configure.mdx` § Best practices for multiple embedding models; `docs/docs/core-components/knowledge-filters.mdx` § Create a filter.
