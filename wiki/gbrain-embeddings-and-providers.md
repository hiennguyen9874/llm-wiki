---
type: Concept
title: GBrain embeddings and providers
description: GBrain's default embedding and reranker models, supported providers, dimension constraints, the gated embedding-migration procedure, and cost and consent controls.
tags: [agent-memory, gbrain, embeddings, providers, cost-control]
status: draft
created: 2026-11-06
stale_after: 2027-02-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:00:00Z }
sources:
  - id: readme
    resource: ../raw/gbrain/README.md
    scope: ../raw/gbrain/
    kind: code
    revision: 27f8b9d
    title: GBrain README (repository root)
  - id: defaults-ts
    resource: ../raw/gbrain/src/core/ai/defaults.ts
    kind: code
    revision: 27f8b9d
    title: AI defaults
  - id: providers-doc
    resource: ../raw/gbrain/docs/integrations/embedding-providers.md
    kind: code
    revision: 27f8b9d
    title: Embedding providers guide
  - id: migrations-doc
    resource: ../raw/gbrain/docs/embedding-migrations.md
    kind: code
    revision: 27f8b9d
    title: Embedding migrations
  - id: migration-guide
    resource: ../raw/gbrain/docs/guides/embedding-migration.md
    kind: code
    revision: 27f8b9d
    title: Embedding migration guide
  - id: embed-cost-cap
    resource: ../raw/gbrain/src/core/embed-cost-cap.ts
    kind: code
    revision: 27f8b9d
    title: Embedding cost cap
  - id: embed-consent
    resource: ../raw/gbrain/src/core/embed-consent.ts
    kind: code
    revision: 27f8b9d
    title: Embedding consent
---

For new installs GBrain defaults to Voyage: embedding model `voyage:voyage-4` at 1,024 dimensions and reranker `voyage:rerank-3-lite`, both set as constants in `src/core/ai/defaults.ts` (the curator confirmed these lines directly).[^defaults-ts] Many other providers are supported, but changing the embedding model or width is deliberately not a config edit: it requires the gated `gbrain migrate embeddings` procedure. See [retrieval pipeline](gbrain-retrieval-pipeline.md) for where embeddings are used.

## Providers (Reported in the provider guide's table)

| Provider | Dims | Notes |
| --- | --- | --- |
| voyage | 1024 | default; $0.06/M tokens |
| openai | 1536 | $0.13/M |
| openrouter | per-model (1536) | $0.02/M |
| google | 768 | $0.025/M |
| azure-openai, minimax | 1536 | — |
| mistral, dashscope, zhipu | 1024 | — |
| ollama | 768 | local, $0 |
| llama-server, LM Studio, litellm | user-set | local or proxy |

Anthropic, DeepSeek and Groq are chat-only. Init auto-detects a provider from available keys; explicit flags win.[^providers-doc][^readme] README also lists Together among embedding providers; the guide's table was not re-checked against it.

## Dimension constraints

Voyage accepts only 256, 512, 1024 or 2048; pgvector HNSW caps at 2,000 dims, so 2,048 falls back to an exact scan. The chunker caps input at `floor(limit × 0.6)` tokens per model (Reported).[^providers-doc] The baseline `schema.sql` still seeds 1536-dim columns and `text-embedding-3-large`, so new-install Voyage 1024 means the column width is set at init, not by the raw DDL (Synthesis).[^defaults-ts]

## Migration rules (Reported)

- `gbrain config set embedding_model|embedding_dimensions` is **refused**. Only `gbrain migrate embeddings --to <model> --dim <N>` (alias `gbrain retrieval-upgrade`) resizes schema, config and vectors, and it is resumable.
- Required sequence: `--status` → `--dry-run` → verified backup and quiesced writers → `--max-cost-usd <finite>` **and** `--yes`. `--yes` does not waive the cap; `spend.posture=tokenmax` does not bypass it.
- A same-width model change still invalidates fact vectors and the semantic cache because the vector space changed. `--no-embed` defers work and is not completion. Image/multimodal vectors are separate.[^migrations-doc][^migration-guide]

## Cost and consent controls (Observed by subagent)

- `embed-cost-cap.ts`: a budget tracker reserves before each send and stops with `BUDGET_STOP_EXIT_CODE`, printing a resume command.[^embed-cost-cap]
- `embedding-migration-budget.ts` refuses with `embedding_budget_below_worst_case` before any request.
- `embed-consent.ts`: explicit backfills need `--yes`, `--max-usd` or pre-approval; queued jobs and write-path embedding are exempt as "the configured feature".[^embed-consent]
- `--timings` reports a per-call cost block (embedding, rerank, expansion, chat, decide) in USD.

## Reranker pricing note

`RETRIEVAL.md` quotes rerank at ~$0.025–0.05/M tokens, while `embedding-pricing.ts` prices `rerank-3-lite` at $0.02 and `rerank-3`/`rerank-2.5` at $0.05 (Observed by subagent); see [discrepancies](gbrain-doc-code-discrepancies.md).

## Relationships

- Used by: [retrieval pipeline](gbrain-retrieval-pipeline.md), [memory model](gbrain-memory-model.md) (fact vectors).
- Privacy implications of configured providers: [memory trust and egress](gbrain-memory-trust-and-egress.md).
- Part of: [GBrain overview](gbrain-overview.md).

[^readme]: `README.md` "Integrations" (Embedding providers, Rerankers bullets).
[^defaults-ts]: `src/core/ai/defaults.ts` lines 15–19 (`DEFAULT_EMBEDDING_MODEL = 'voyage:voyage-4'`, `DEFAULT_EMBEDDING_DIMENSIONS = 1024`, `DEFAULT_RERANKER_MODEL = 'voyage:rerank-3-lite'`).
[^providers-doc]: `docs/integrations/embedding-providers.md` TL;DR table, "Choosing dimensions", "Per-input token caps".
[^migrations-doc]: `docs/embedding-migrations.md` "Preview, authorize, then verify".
[^migration-guide]: `docs/guides/embedding-migration.md` "What it does, in order".
[^embed-cost-cap]: `src/core/embed-cost-cap.ts` (BudgetTracker, `BUDGET_STOP_EXIT_CODE`).
[^embed-consent]: `src/core/embed-consent.ts`.
