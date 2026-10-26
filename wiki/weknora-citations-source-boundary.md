---
type: Concept
title: WeKnora citations and model-facing source boundary
description: Request-local source handles, original-chunk evidence restoration, citation expansion, and prompt-level untrusted-data rules already exist in WeKnora.
tags: [rag, weknora, citations, security]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T16:19:21Z }
stale_after: 2027-01-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a2586fd58
    title: WeKnora v0.8.3 repository snapshot
---

**Observed:** WeKnora already has a request-scoped model-context registry, restoration of original citation source bodies after context expansion, a private-to-public citation protocol, and an explicit untrusted-source instruction. **Synthesis:** an uncompiled citation row in an older comparison is not a missing implementation; importing a second evidence registry before testing this one would duplicate an existing boundary. None of these mechanisms establishes claim entailment or runtime prompt-injection resistance.[^weknora]

## Expanded retrieval context is not automatically source evidence

`PluginMerge.attachCitationSources` collects original chunks for rewritten/merged results, including related image OCR/caption chunks. Candidates must be enabled, nonempty, in the result's document and KB, and not hidden parent-text chunks; additional relatedness/content checks constrain inclusion. It copies source locators, content revision, offsets and other original chunk fields into individual citation sources.[^weknora]

`expandCitationSources` deduplicates by chunk ID and omits a rewritten result when source lookup yielded no citation sources. **Synthesis:** the inspected code intentionally avoids presenting a neighbouring paragraph under a child's identity. Repository lookups and every authorization caller were not audited end-to-end.[^weknora]

## Request-local registry and public citations

`prepareMessagesWithModelContext` expands citation sources, registers search results, renders model-facing knowledge/web rows, and adds the registry-owned protocol. When rendered source bodies cannot be established, it tells the model not to cite or infer from unavailable evidence.[^weknora]

`modelcontext.Registry` composes source/resource/issue/MCP handle tables. Source handles use `chunk://N`, `doc://N`, `kb://N` and `url://N`; persistent workspace references can use `weknora://` URIs rather than keeping a request-local number. The citation prompt distinguishes current evidence from historical/navigation handles and restricts citations to supplied supporting chunks or web sources.[^weknora]

**Observed:** `sourceRegistry.ExpandText` drops model-authored public `<kb>`/`<web>` tags and expands accepted private `<ref>` tags through registered, currently citable handles. Unknown/noncitable handles produce no citation. `citationStreamExpander` buffers partial source tags rather than exposing incomplete private tags. This is formatting/identity enforcement, not a semantic support checker.[^weknora]

## Untrusted-source instructions and remaining hardening work

`prepareMessagesWithHistory` appends `SourceDataBoundaryPrompt` even when a custom/intent prompt is supplied. The instruction explicitly treats documents, attachments, KB metadata, retrieved passages, web pages and tool results as untrusted data that cannot grant permissions or replace the user's task. `prompt_boundary_test.go` asserts preservation under default and override prompts; it was read, not executed.[^weknora]

**Synthesis:** [OpenRAG's escaped untrusted-text delimiters](openrag-hybrid-retrieval.md) are a useful test/design reference, not evidence that WeKnora lacks a source boundary. This pass did not establish equivalent delimiter escaping across all WeKnora renderers, tool authorization paths, agent lifecycles, or public streaming consumers. Test those boundaries before replacing or adding a wrapper.

## Relationships

- **Uses:** [hybrid retrieval and context expansion](weknora-hybrid-retrieval.md) as candidate inputs, but restores original identities for citations.
- **Complements:** [security controls](weknora-security.md); prompt instructions do not authorize tool calls.
- **Related:** [RAGFlow citations](ragflow-citations.md) distinguish evidence identity from post-hoc similarity insertion; neither is proof of entailment.
- **Informs:** [the selective fork roadmap](weknora-fork-roadmap.md), which preserves this implementation rather than assuming citations are absent.

## Coverage limits

Selected static regions only: citation-source restoration and pipeline reference preparation were read in full; registry/source codecs and prompt preparation were sampled; citation expansion/stream helper bodies were inspected. The rest of `modelcontext/`, actual renderer escaping, frontend consumption, agent registry wiring, SSE reconnect behavior, and citation tests remain unverified. No upstream imports, builds, tests, services or model calls ran. See [coverage](weknora-source-map.md).

[^weknora]: Revision `fd7a2586fd58`, package entry [README](../raw/WeKnora/README.md); `internal/application/service/chat_pipeline/citation_sources.go::PluginMerge.attachCitationSources, expandCitationSources`; `chat_pipeline/references.go::prepareMessagesWithModelContext, orderedPipelineReferences`; `chat_pipeline/common.go::prepareMessagesWithHistory`; `chat_pipeline/prompt_boundary_test.go::TestSourceBoundarySurvivesNormalAndIntentCustomPrompts` (test intent only); `internal/types/prompt_instructions.go::SourceDataBoundaryPrompt, SourcedAnswerOutputPrompt`; `internal/modelcontext/registry.go::Registry, NewRegistry, ProtocolPrompt`; `modelcontext/sources.go::RegisterSearchResults`; `modelcontext/source_text.go::DecodeDurableText, EncodeDurableURIs, ExpandHandleText`; `modelcontext/citations.go::citationEnabledProtocolPrompt, ExpandText, citationTag, citationStreamExpander.Feed, Flush`.
