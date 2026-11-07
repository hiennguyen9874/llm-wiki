---
type: Concept
title: Headroom compression pipeline
description: Content-aware compression, pipeline safeguards, and implementation-specific defaults in Headroom.
tags: [agent-memory, context-compression]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:19:57Z }
stale_after: 2027-05-06
sources:
  - id: headroom
    resource: ../raw/headroom/README.md
    scope: ../raw/headroom/
    kind: code
    revision: 2b0315b
    title: Headroom repository
---

**Observed:** the Python transform pipeline optionally applies tool-result interceptors, then CacheAligner when enabled, and then ContentRouter. The router selects strategies by content, including JSON, code, logs, search and HTML. CacheAligner detects volatile prefix content rather than rewriting it.[^headroom]

- The library `compress()` returns original messages on an exception and reverts an inflationary result. The pipeline also has a circuit breaker; a passthrough result is not evidence that compression succeeded.[^headroom]
- Routing includes lossless-first processing and guards against accepting certain lossy results without a retrievable marker. User messages and certain tools receive protection, subject to configuration; library and proxy profiles have different defaults.[^headroom]
- Repeated data can compress substantially, whereas the README says dense prose may compress little. Quality, latency, and savings are workload-dependent and were not independently tested here.[^headroom]

## Relationships

- Uses [prefix caching and CCR](headroom-cache-and-ccr.md) to preserve provider-cache behavior and support recovery.
- [Benchmarks](headroom-benchmarks.md) separates vendor-reported measurements from reproduced results.

[^headroom]: `headroom/transforms/pipeline.py::TransformPipeline._build_default_transforms`, `TransformPipeline.apply`; `headroom/transforms/cache_aligner.py` module header; `headroom/transforms/content_router.py::ContentRouter._apply_strategy_to_content`, `_compress_block_content`, `ContentRouterConfig`; `headroom/compress.py::compress`; `README.md` §§ Proof, When to use; revision `2b0315b`.
