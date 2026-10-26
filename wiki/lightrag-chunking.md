---
type: Concept
title: LightRAG chunking strategies and provenance
description: Fixed, recursive, vector-semantic, paragraph-semantic and custom dispatch, persisted parameters, and fallback and source-span limits.
tags: [rag, chunking, parsing]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:55:00Z }
stale_after: 2027-01-24
sources:
  - id: lightrag-aaebfe1
    resource: ../raw/LightRAG/README.md
    scope: ../raw/LightRAG/
    kind: code
    revision: aaebfe1
    title: LightRAG repository
---

**Observed:** per-file processing supports fixed (`F`), recursive (`R`), vector-semantic (`V`), paragraph-semantic (`P`), and a custom/legacy (`C`) dispatch selector. The four standard strategies use a normalized file-chunker contract when explicitly selected; no selector can preserve legacy `chunking_func` behavior. **Synthesis:** overriding a global chunking callable does not intercept every explicit file-strategy choice.[^lightrag-aaebfe1]

## Dispatch and durable parameters

**Observed:** parser routing validates at most one distinct chunk selector. Per-document chunk parameters are resolved at enqueue and stored; only the selected strategy's parameter block needs to survive. Explicit F/R/V/P paths receive standardized snapshot kwargs rather than invoking `chunking_func`. C uses the legacy six-argument callable; selecting it with the default implementation warns and falls back to fixed behavior. Plugins use the `lightrag.chunkers` entry-point group.[^lightrag-aaebfe1]

| Strategy | Observed behavior and constraints |
| --- | --- |
| F | Default 1,200 tokens / 100 overlap; negative overlap or overlap ≥ chunk size raises. Character-only splitting can raise on token overflow. Unlocatable text spans degrade to absent spans rather than fabricated positions. |
| R | Recursive separator cascade configured by bounded separator lists; the default includes paragraphs, lines, Chinese punctuation, spaces, and character fallback. Full splitter body was not inspected. |
| V | Uses semantic-vector segmentation; missing embedding callable falls back to R, while missing `langchain-experimental` raises. Oversized segments are re-split by R with zero overlap; target size is not an unconditional hard promise. |
| P | Uses blocks sidecars to preserve document headings/paragraph/table structure; missing/unreadable blocks fall back to R. Table splitting has row/character/recursive degradation paths; reference-block dropping is opt-in. Default target size is 2,000. |

**Observed:** the recursive fallback requires its optional splitter dependency. Persisted vector sentence-split regex is discarded in favor of a live configured value; the source cites regex-security concerns. **Synthesis:** “frozen document parameters” has deliberate security exceptions, so it is not a guarantee that old serialized arbitrary expressions are executed again.[^lightrag-aaebfe1]

## Chunk identity and retrieval provenance

**Observed:** chunk IDs normally take `{doc_id}-chunk-{order:03d}`, with a hash fallback for collisions. Source spans may be absent when exact alignment cannot be established. Headings and multimodal markup treatment have downstream extraction/rendering rules; a chunk boundary or page/heading hint is not independent validation that the answer cites the correct source.[^lightrag-aaebfe1]

## Documentation reconciliation

**Reported:** README advertises four strategies. **Observed:** grammar also implements C/custom dispatch, which is a compatibility extension rather than a fifth demonstrated semantic algorithm. SDK guide defaults also drift: embedding batch/concurrency examples differ from current constants. Use inspected defaults for this pin, not unqualified documentation examples.[^lightrag-aaebfe1]

## Relationships

- **Used by:** [Ingestion](lightrag-ingestion.md).
- **Depends on:** [Parser sidecars](lightrag-parsing-multimodal.md) for P's structure-aware path and [embedding models](lightrag-models.md) for V.
- **Produces:** Source chunks consumed by [extraction](lightrag-extraction.md) and [retrieval](lightrag-retrieval.md).

## Evidence limits

Static targeted reads of fixed/vector/paragraph implementations and dispatch. Recursive implementation and full plugin loading were not audited; no document splitting, golden fixtures, embedding calls, span accuracy or table-quality evaluation ran. See [coverage](lightrag-source-map.md).

[^lightrag-aaebfe1]: Revision `aaebfe1`: `lightrag/pipeline.py` chunk dispatch (5130–5150); `parser/routing.py::ProcessOptions, validate_process_options, resolve_chunk_options`; `constants.py` chunk defaults, selectors and separator bounds; `chunker/token_size.py::chunking_by_token_size, chunking_by_fixed_token`; `chunker/semantic_vector.py::chunking_by_semantic_vector`; `chunker/paragraph_semantic.py::chunking_by_paragraph_semantic` and table-splitting helpers; `chunker/plugins.py` entry-point group (symbol inspection); `utils_pipeline.py::build_chunks_dict_from_chunking_result` and live sentence-regex handling (117–139); README “Multiple Text Chunking Strategies”; `docs/ParagraphSemanticChunking.md`; `docs/ProgramingWithCore.md` defaults table.
