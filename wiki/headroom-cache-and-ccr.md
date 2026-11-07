---
type: Concept
title: Headroom prefix caching and CCR
description: Provider-prefix preservation, compression-result caching, and bounded retrieval of original content.
tags: [agent-memory, context-compression, caching]
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

**Observed:** Headroom separately caches compression results and tracks provider-confirmed prefix caching. The Python session engine can replay previously forwarded prefix bytes to preserve cache identity; ContentRouter maintains its own result cache. These are distinct from caching whole responses.[^headroom]

## Compress-cache-retrieve

CCR stores original content and emits a retrieval marker; the proxy can inject `headroom_retrieve` when it recognizes an owned marker and handle retrieval calls. Python's default CCR TTL constant is 1,800 seconds, with bounded capacity; the proxy normally uses a SQLite backend, while stateless operation avoids that disk store. Expiry, eviction, store errors, and missing markers limit recovery, so reversibility is not an unconditional guarantee.[^headroom]

Python and Rust CCR use different key and expiry implementations; the SmartCrusher bridge mirrors Rust entries under the emitted hash in the Python store. A Python class docstring still states 300 seconds, contradicting the 1,800-second constant and constructor documentation.[^headroom]

## Relationships

- Supports [compression](headroom-compression.md); storage and content exposure are covered by [privacy](headroom-privacy-and-security.md).

[^headroom]: `headroom/cache/prefix_tracker.py::PrefixCacheTracker`, `overlay_cached_prefix`; `headroom/proxy/session_engine.py::prepare_turn`, `finalize_turn`; `headroom/transforms/content_router.py::CompressionCache`; `headroom/cache/compression_store.py::DEFAULT_CCR_TTL_SECONDS`, `CompressionStore`, `_create_default_ccr_backend`; `headroom/ccr/tool_injection.py::CCRToolInjector`, `headroom/ccr/response_handler.py::CCRResponseHandler`; `crates/headroom-core/src/ccr/mod.rs::compute_key`; `headroom/transforms/smart_crusher.py::SmartCrusher._mirror_ccr_to_python_store`; revision `2b0315b`.
