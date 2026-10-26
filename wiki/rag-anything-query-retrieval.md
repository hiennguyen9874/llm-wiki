---
type: Concept
title: RAG-Anything query and retrieval
description: Text queries, attachment-to-text query enhancement, retrieved-image VLM answering, cache keys, and image-access boundaries.
tags: [ml, rag, retrieval, vision]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:43:55Z }
stale_after: 2027-01-24
sources:
  - id: rag-anything-3a14ecb
    resource: ../raw/RAG-Anything/README.md
    scope: ../raw/RAG-Anything/
    kind: code
    revision: 3a14ecb66fb352b90d40a9884a5ad235d98ac72e
    title: RAG-Anything repository
---

**Observed:** RAG-Anything offers three related but distinct query mechanisms: LightRAG text retrieval, descriptions of query-side attachments appended to the query, and VLM answering over image files named in retrieved context. Providing a vision function enables the retrieved-image path by default. **Synthesis:** neither query-side attachment analysis nor retrieved-image answering establishes a separate multimodal vector ranking algorithm.[^rag-anything-3a14ecb]

## Query paths

| API | Observed mechanism |
| --- | --- |
| `aquery` / synchronous `query` | Builds LightRAG `QueryParam`; defaults `vlm_enhanced` to whether `vision_model_func` exists; accepts explicit `vlm_enhanced=False` |
| `aquery_with_multimodal` | Describes supplied image/table/equation/generic items, appends the descriptions and query-enhancement suffix to the query string, then calls `aquery` |
| `aquery_vlm_enhanced` | Retrieves LightRAG's prompt without its final answer, identifies local image paths, constructs multimodal messages, and calls the vision function |

**Observed:** `mode` is forwarded to LightRAG (`mix` by default in these APIs); README examples also use `hybrid`, `local`, `global`, and `naive`. Their ranking semantics belong to the external LightRAG version, not an independently inspected implementation in this source.[^rag-anything-3a14ecb]

## Retrieved-image answering

**Observed:** `aquery_vlm_enhanced` bypasses image processing for `mode="bypass"`, `only_need_context`, and `only_need_prompt`. Otherwise it performs a prompt-only retrieval, scans `Image Path:` lines ending in supported image extensions, and replaces valid paths with markers plus image payloads in OpenAI-style messages. MIME type comes from image bytes, not an unconditional JPEG label.[^rag-anything-3a14ecb]

- When no images survive, it performs another ordinary LightRAG query. **Synthesis:** this can duplicate retrieval work; configuring vision can change costs even for text-only answers.
- `stream=True` can return the vision function's async iterator rather than a string. Custom adapters must accept and forward streaming options.
- The initial prompt-only retrieval does not receive the caller's `system_prompt`; the final VLM message appends it to a fixed system instruction. **Synthesis:** a custom LightRAG answer template is not used with identical semantics on this path.
- Audio/video chunk templates use `Source:`, not `Image Path:`. **Synthesis:** their content is retrieved as transcript/description text; this path does not automatically reopen a video or revisit its keyframes.[^rag-anything-3a14ecb]

## Attachment-query cache

**Observed:** `aquery_with_multimodal` builds a `multimodal_query:<md5>` key over stripped query, mode, normalized content, and forwarded arguments. Local file contents contribute SHA-256 fingerprints; long table representations are hashed. Callable overrides include module/qualified name/object identity. Retrieval flags are included, preventing context-only responses from sharing a key with ordinary answers.[^rag-anything-3a14ecb]

The cache uses LightRAG `llm_response_cache` when enabled and flushes through its callback. Streaming results are not cached. The retrieved-image VLM path has no separate final-answer cache of its own; this does not rule out caches in external provider adapters or LightRAG.[^rag-anything-3a14ecb]

## Image-access and disclosure boundary

**Observed:** retrieved-image validation requires an existing image, supported extension/signature, size at most 50 MB, and no symlink file. Resolved paths must be inside the current working directory, configured working/output directories, or explicitly allowed `extra_safe_dirs`. Encoding rechecks magic bytes before sending data.[^rag-anything-3a14ecb]

**Synthesis:** this narrows arbitrary-file exfiltration from malicious `Image Path:` text, but it is not a full prompt-injection defense: retrieved prose remains model input, and allowed images are disclosed to the configured vision provider. An overly broad working directory or `extra_safe_dirs` weakens confinement. Query-side and ingestion-side image loading should not be assumed to share this exact directory allowlist.[^rag-anything-3a14ecb]

## Relationships

- **Depends on:** [Multimodal grounding](rag-anything-multimodal-grounding.md) for descriptions, anchors, and image-path chunk templates.
- **Uses:** [Audio/video processing](rag-anything-audio-video.md) through its text retrieval surface, not native media replay.
- **Depends on:** [Runtime stack](rag-anything-stack-operations.md) for provider adapters and LightRAG compatibility.
- **Compared by:** [Reproduction and evaluation](rag-anything-reproduction-evaluation.md), whose query script explicitly disables VLM enhancement.

## Evidence limits

No retrieval/provider call, stream, cache hit, or security exploit was executed. Retrieval quality and README modality-ranking claims are unverified. See [source map](rag-anything-source-map.md).

[^rag-anything-3a14ecb]: Revision `3a14ecb66fb352b90d40a9884a5ad235d98ac72e`: `raganything/query.py::_fingerprint_local_file` (33), cache normalization/key helpers (65–132), `aquery` (134), `aquery_with_multimodal` (227–355), `aquery_vlm_enhanced` (390–476), `_process_multimodal_query_content` (477), `_process_image_paths_for_vlm` (652–768), `_build_vlm_messages_with_images` (771), `_call_vlm_with_multimodal_content` (863); `utils.py::encode_image_to_base64` (528), `validate_image_file` (551); `image_signature.py::image_mime_type`; `prompt.py` chunk templates (336–364) and query suffix (414); `processor.py` audio/video templates (1453–1478); README “Query Options”; tests `test_vlm_query_flags.py`, `test_multimodal_query_key.py`, `testquery_stream_cache.py` (inspected, not run).
