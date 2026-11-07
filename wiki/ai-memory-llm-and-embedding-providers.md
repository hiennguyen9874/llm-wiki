---
type: Concept
title: ai-memory LLM and embedding providers
description: Supported LLM and embedding providers in ai-memory, fallback and circuit-breaker rules, per-task profiles, and the default local MiniLM embedder.
tags: [agent-memory, ai-memory, llm, embeddings, providers]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
stale_after: 2027-02-06
sources:
  - id: readme
    resource: ../raw/ai-memory/README.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory README
  - id: llm-providers
    resource: ../raw/ai-memory/docs/llm-providers.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: LLM providers
  - id: llm-fallback
    resource: ../raw/ai-memory/docs/llm-provider-fallback.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: LLM provider fallback
  - id: local-embeddings
    resource: ../raw/ai-memory/docs/local-embeddings.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Local embeddings
  - id: llm-code
    resource: ../raw/ai-memory/crates/ai-memory-llm/src/factory.rs
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory-llm (factory.rs, fallback.rs, local.rs)
---

# ai-memory LLM and embedding providers

LLM and embedding providers are strictly optional: everything works with zero LLM calls, and a provider upgrades session summaries and enables semantic search.[^readme] Provider names, fallback logic and defaults change quickly between releases, so the model identifiers are intentionally not recorded here.

Evidence class: **Observed** (docs plus `factory.rs`/`fallback.rs`/`local.rs`, delegated static reading); nothing executed. `stale_after` is set.

## Providers

- **LLM (10 choices in `ProviderChoice`):** anthropic, anthropic-oauth, openai, openai-oauth, codex (Codex CLI credential reuse), copilot, cursor, gemini, openai-compat (Ollama, LM Studio, vLLM), opencode (Go and Zen).[^llm-code][^readme]
- **Embedders (6 in `EmbedderChoice`):** openai, voyage, google, openai-compat, local, copilot. Each stored vector carries `(provider, model, dim)`; a dim mismatch is refused.[^llm-code]
- **Recommended LLM default** per `llm-providers.md` is an Anthropic Haiku-class model, which conflicts with a verdict in `llm-provider-comparison.md` (see [Source map](ai-memory-source-map-and-doc-discrepancies.md)).[^llm-providers]

## Fallback

`llm_fallbacks` advance only on transient errors (429, 5xx, timeout, connect); deterministic 4xx and schema failures stop. Each entry has a circuit breaker with a 30 s cooldown extended by `Retry-After`/Google `RetryInfo.retryDelay`, clamped to 1 h. The same request, schema and operation id go to every candidate. Per-task profiles `[llm.<task>]` exist for consolidation, bootstrap, auto_improve, experience, dream, lint, profile, rerank and query_answer, with no inherited global fallbacks; health is passive with no probing.[^llm-fallback][^llm-code]

## Local embeddings

`all-MiniLM-L6-v2`, 384 dimensions, pure-Rust candle, ~87 MB, three sha256-pinned files, downloaded on first start. It is the effective default when no provider is set (`"none"` opts out). Concurrency is half the cores clamped to 2–6; queries wait 250 ms before falling back to lexical search; inputs are truncated at 512 tokens.[^local-embeddings][^llm-code]

## Relationships

- Consumers: [Retrieval pipeline](ai-memory-retrieval-pipeline.md) (vector stream, rerank, answer), [Consolidation](ai-memory-consolidation-and-aging.md), [Auto-improvement](ai-memory-auto-improvement.md).
- Egress consequences of cloud providers: [Data handling](ai-memory-data-handling-and-lifecycle-ops.md).

[^readme]: `../raw/ai-memory/README.md` — "LLM providers"; "Everyday use" (`ai-memory status --json` per-workload telemetry).
[^llm-providers]: `../raw/ai-memory/docs/llm-providers.md` — provider configuration and recommended default.
[^llm-fallback]: `../raw/ai-memory/docs/llm-provider-fallback.md` — transient vs deterministic classification, circuit breaker, task profiles.
[^local-embeddings]: `../raw/ai-memory/docs/local-embeddings.md` — model, size, capacity, defaults (internally inconsistent about "opt-in" for existing installs).
[^llm-code]: `../raw/ai-memory/crates/ai-memory-llm/src/factory.rs::ProviderChoice, EmbedderChoice`; `src/fallback.rs`; `src/local.rs::LOCAL_MODEL`; `crates/ai-memory-cli/src/config.rs` (default-to-local at ~line 3265, reported by delegate).
