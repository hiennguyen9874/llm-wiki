---
okf_version: "0.2"
---

# LLM Wiki

The complete retrieval map for compiled knowledge. See [LLM Wiki Contract](../AGENTS.md) for storage and maintenance rules.

## Agent memory — ai pages (compiled by a concurrent ingest)

- [ai-memory architecture and crates](ai-memory-architecture.md) — Data flow, 11-crate layout, SQLite single-writer storage, data directory and the cross-cutting invariants of ai-memory 3.4.2.
- [ai-memory authentication, authorization and security model](ai-memory-auth-and-security.md) — Loopback-by-default deployment, the bearer-token ladder, user API keys, per-project grants, admission webhooks, HTTPS posture and known security caveats of ai-memory.
- [ai-memory auto-improvement loop, eval gates and rules promotion](ai-memory-auto-improvement.md) — The scheduled auto-improvement loop that stages and applies page proposals, its optional eval gate, and the not-yet-implemented rules-promotion design.
- [ai-memory capture, hooks and privacy boundary](ai-memory-capture-and-hooks.md) — How ai-memory silently captures agent lifecycle events via fire-and-forget hooks, spools them offline, sanitizes them at a typed boundary, and applies per-repository capture policy.
- [ai-memory consolidation, aging and dream](ai-memory-consolidation-and-aging.md) — How ai-memory turns sessions into pages (zero-LLM by default), and its decay formula, compaction, dedup, contradiction flagging, belief strength and opt-in dream pass.
- [ai-memory data handling, retention and lifecycle operations](ai-memory-data-handling-and-lifecycle-ops.md) — What ai-memory stores, its opt-in network egress paths, retention and deletion semantics, and the safety matrix for purge, merge, backup, restore, reset and reindex.
- [ai-memory distribution, CI, companions and contributor rules](ai-memory-distribution-ci-and-companions.md) — How ai-memory is packaged and released (install scripts, brew, AUR, RPM, Scoop, Nix, Docker, macOS app), its CI workflows, companion projects, and contributor gates.
- [ai-memory evals and LongMemEval-S benchmarks](ai-memory-evals-and-benchmarks.md) — The ai-memory-eval harness subcommands and the published LongMemEval-S retrieval results (3.4.0 hit@5 0.951 FTS / 0.940 local), with protocol, trend and caveats.
- [ai-memory handoffs and agent messaging](ai-memory-handoffs-and-messaging.md) — The claim-once handoff protocol between agent sessions, the offer-not-claim option, and the directed claim-once agent-to-agent message inbox.
- [ai-memory harness integrations, install flow and CLI](ai-memory-harness-integrations-and-cli.md) — Which agent harnesses ai-memory supports, the three integration shapes, setup/run/install-hooks flows, and the CLI subcommand surface.
- [ai-memory LLM and embedding providers](ai-memory-llm-and-embedding-providers.md) — Supported LLM and embedding providers in ai-memory, fallback and circuit-breaker rules, per-task profiles, and the default local MiniLM embedder.
- [ai-memory managed workstreams (ai-memory run)](ai-memory-managed-workstreams.md) — How ai-memory run provides cross-harness session continuity through leases, a ledger, a private local history dossier, and degraded-offline recovery.
- [ai-memory MCP tools and HTTP surfaces](ai-memory-mcp-tools-and-http-surfaces.md) — The 27 memory_* MCP tools, the /web and /api/v1 HTTP surfaces, opt-in serve flags, and localization of the web UI.
- [ai-memory overview](ai-memory-overview.md) — Entry point to ai-memory, a Rust single-binary long-term memory server for AI coding agents that stores memory as a git-backed markdown wiki and works with zero LLM calls by default.
- [ai-memory project identity, marker file, auto-scope and cross-project profile](ai-memory-project-identity-and-profile.md) — How ai-memory decides which project a session belongs to (marker file, auto_scope) and how a small cross-project profile of user habits is injected as defaults.
- [ai-memory retrieval pipeline](ai-memory-retrieval-pipeline.md) — How memory_query fuses FTS, entity, vector, graph and observation streams with RRF, applies filters, authority adjustments and optional answer synthesis.
- [ai-memory self-reported comparison with other agent-memory tools](ai-memory-comparison-claims.md) — What the ai-memory README and comparison doc claim relative to Mem0, Zep, basic-memory, Hindsight, Claude Code memory and others, labelled as self-reported and point-in-time.
- [ai-memory source map, coverage ledger and documentation discrepancies](ai-memory-source-map-and-doc-discrepancies.md) — Coverage ledger for the ai-memory snapshot ingested on 2026-11-06 (what was inspected, excluded or pending) and the doc-versus-code discrepancies found.
- [ai-memory wiki storage, OKF mapping, typed edges and temporal queries](ai-memory-wiki-storage-and-okf.md) — How ai-memory stores pages (tiers, kinds, versioning, git checkpoints), maps frontmatter to OKF v0.2, models typed edges, and answers as_of queries.

## Agent memory — cmb pages (compiled by a concurrent ingest)

- [CMB — Coding Memory Benchmark](cmb-coding-memory-benchmark.md) — Benchmark design and reported results of CMB (long-horizon, interleaved coding-agent memory) and its TriLink method, as shipped as a PDF in the Hy-Memory repo.

## Agent memory — Cognee

- [Cognee ingestion and code graphs](cognee-ingestion-and-code-graphs.md) — How Cognee stages and indexes content, builds knowledge graphs, and extracts repository structure.
- [Cognee interfaces and deployment](cognee-interfaces-and-deployment.md) — Python, HTTP, CLI, MCP, and container deployment surfaces with configuration caveats.
- [Cognee overview](cognee-overview.md) — Cognee's graph-based agent memory model, public operations, local quickstart, and source snapshot.
- [Cognee reported benchmarks](cognee-benchmarks.md) — Reported BEAM conversational-memory scores and methodological limits at the inspected Cognee snapshot.
- [Cognee retrieval and query routing](cognee-retrieval.md) — Recall versus search, routing rules, retrieval lanes, and dataset-scoped fallback behavior.
- [Cognee sessions and improvement](cognee-sessions-and-improvement.md) — Session cache, ordered improvement stages, distillation, and deletion-invalidation limits.
- [Cognee source map and coverage limits](cognee-source-map.md) — Coverage ledger, static-inspection boundaries, and pending work for the Cognee repository snapshot.
- [Cognee storage, authorization, and deletion](cognee-storage-and-security.md) — Store families, authentication posture, local file boundaries, and deletion limitations in Cognee.

## Agent memory — gbrain pages (compiled by a concurrent ingest)

- [GBrain architecture and engines](gbrain-architecture-and-engines.md) — How GBrain's single operation registry, BrainEngine contract, PGLite and Postgres engines, topologies, thin client, canonical writers and generations fit together.
- [GBrain authorization and security model](gbrain-authorization-and-security.md) — GBrain's OAuth and token model, scopes and grants, the checks run per request, what does and does not confine callers, and its install, environment and hook trust boundaries.
- [GBrain CLI and MCP surface](gbrain-cli-and-mcp-surface.md) — How GBrain's CLI dispatches commands, how the MCP server exposes tools over stdio and HTTP with surface ceilings, and how gbrain setup wires harnesses and brain-first instructions.
- [GBrain data model and system of record](gbrain-data-model-and-system-of-record.md) — GBrain's brain-vs-source axes, core tables, page anatomy (frontmatter, compiled truth, facts fence, timeline), size ceilings, schema packs and what is canonical Markdown versus DB-only.
- [GBrain doc/code discrepancies](gbrain-doc-code-discrepancies.md) — Consolidated list of places where GBrain's documentation, comments and code disagree or are stale at revision 27f8b9d, with which side the evidence favors.
- [GBrain dream cycle and autopilot](gbrain-dream-cycle-and-autopilot.md) — The 31-phase maintenance cycle behind gbrain dream, autopilot and the autopilot-cycle job, including locking, scheduling, health checks and quiet hours.
- [GBrain embeddings and providers](gbrain-embeddings-and-providers.md) — GBrain's default embedding and reranker models, supported providers, dimension constraints, the gated embedding-migration procedure, and cost and consent controls.
- [GBrain evals and reported benchmarks](gbrain-evals-and-benchmarks.md) — The eval suites shipped with GBrain, what each measures, and every headline number with its protocol, locator and evidence class (almost all Reported, not reproduced here).
- [GBrain knowledge graph and think](gbrain-knowledge-graph.md) — How GBrain extracts typed links without LLM calls, walks them breadth-first, uses them in retrieval and ranking, and how the think verb synthesizes cited answers.
- [GBrain memory model](gbrain-memory-model.md) — The remember/recall/forget verb protocol and how facts, takes, beliefs, pages and core memory differ, including corrections, withdrawal and the compiled-truth plus timeline convention.
- [GBrain memory trust, egress and contradictions](gbrain-memory-trust-and-egress.md) — GBrain's six trust tiers, write-gate defaults, what text leaves the machine (including the Memorable relay consent model), and its contradiction-detection and calibration mechanisms.
- [GBrain Minions job queue](gbrain-minions-job-queue.md) — How GBrain's Postgres-native Minions queue stores jobs, moves them through states, survives worker crashes, runs shell jobs and gates quiet hours.
- [GBrain overview](gbrain-overview.md) — What Garry Tan's GBrain agent-memory system is, how its repository is laid out, and where each subsystem is documented in this wiki.
- [GBrain recipes, plugins and personal-agent bootstrap](gbrain-recipes-plugins-and-bootstrap.md) — GBrain's integration recipes, the Claude Code and Codex plugin lanes and variants, and the bootstrap flow that turns a coding-agent session into a persistent personal agent.
- [GBrain retrieval pipeline](gbrain-retrieval-pipeline.md) — Stage order, search modes, reranking, readiness and failure behavior of GBrain's hybrid search, plus what text reaches providers.
- [GBrain skills, resolver and conventions](gbrain-skills-and-resolver.md) — How GBrain teaches agents through 75 Markdown skills, the RESOLVER routing map, filing, output and friction conventions, and the tooling that creates, optimizes and distributes skills.
- [GBrain source map](gbrain-source-map.md) — Coverage ledger for the GBrain repository snapshot, listing every top-level artifact as inspected, sampled, excluded or pending so future ingests can be idempotent.
- [GBrain sync, ingestion, enrichment and open loops](gbrain-sync-and-ingestion.md) — How GBrain syncs Markdown repos into its index (with soft deletes), ingests from native source kinds and connectors, enriches entities, and tracks open loops from email.
- [GBrain testing, CI, release and repository hygiene](gbrain-testing-ci-and-release.md) — GBrain's test lanes and commands, CI and guard battery, versioning and release gating, community-PR wave process, TLA+ drain-lease spec, vendored code and notable repo-hygiene findings.

## Agent memory — Headroom

- [Headroom compression pipeline](headroom-compression.md) — Content-aware compression, pipeline safeguards, and implementation-specific defaults in Headroom.
- [Headroom failure and traffic learning](headroom-learning.md) — Offline session analysis, loop detection, managed-file writing, and the distinct online traffic learner.
- [Headroom interfaces and deployment](headroom-interfaces.md) — Library, proxy, agent wrapper, MCP, and packaging entry points and their operating boundaries.
- [Headroom memory architecture and retrieval](headroom-memory.md) — Hierarchical memory, persistence, project partitioning, retrieval, and injection in Headroom.
- [Headroom overview](headroom-overview.md) — Headroom's context-compression product, interfaces, packaging, and snapshot boundaries.
- [Headroom prefix caching and CCR](headroom-cache-and-ccr.md) — Provider-prefix preservation, compression-result caching, and bounded retrieval of original content.
- [Headroom privacy and security boundaries](headroom-privacy-and-security.md) — Telemetry defaults, local plaintext storage, control-surface trust, and documentation discrepancies.
- [Headroom reported benchmarks and tests](headroom-benchmarks.md) — Reported context-compression savings, benchmark methodology differences, and unexecuted test coverage.
- [Headroom source map and coverage limits](headroom-source-map.md) — Static-inspection ledger, package identity, exclusions, and outstanding coverage for the Headroom snapshot.

## Agent memory — Hindsight (`raw/hindsight`, revision `eb963cb`; start at the overview)

- [Hindsight API surface, services and packaging](hindsight-api-surface.md) — Hindsight's server entry points (REST, MCP, worker, admin CLI), async operations, and how the api, api-slim, all, all-slim and all-npm packages differ.
- [Hindsight benchmarks, evals and test suites](hindsight-benchmarks-and-testing.md) — Hindsight's published benchmark claims and their provenance, the in-repo system evals, blackbox system tests and other test suites.
- [Hindsight clients, CLI, embed daemon and dev tooling](hindsight-clients-cli-embed.md) — Hindsight's Python/TypeScript/Go/Rust SDKs and how they are generated, the Rust CLI, the hindsight-embed local daemon, and hindsight-dev tooling.
- [Hindsight coding-agents integration](hindsight-coding-agents.md) — How the @vectorize-io/hindsight-coding-agents package gives CLI coding agents per-repo memory from git history, session transcripts and seeded knowledge pages.
- [Hindsight consolidation, observations, mental models and knowledge pages](hindsight-consolidation-and-mental-models.md) — How Hindsight consolidates facts into evidence-backed observations and maintains mental models and knowledge pages as living, auto-refreshed synthesis.
- [Hindsight contributor workflow and security policy](hindsight-contributor-workflow.md) — Hindsight's repo rules for development, linting, testing, generated files, configuration changes, releases, pull requests and vulnerability reporting.
- [Hindsight control plane](hindsight-control-plane.md) — The Next.js web UI for Hindsight: stack, views, how it proxies to the API, authentication and environment variables.
- [Hindsight decision models](hindsight-decision-models.md) — Hindsight's small open-weight models (hs-decide-1-flash, hs-rerank-1, hs-embed-1) that replace LLM judgments inside recall, consolidation, reflect and pages.
- [Hindsight deployment, monitoring and CI/release](hindsight-deployment-and-ci.md) — How Hindsight is deployed (Docker targets, compose variants, Helm), monitored (Prometheus metrics, Grafana dashboards) and released through GitHub Actions.
- [Hindsight documentation vs code discrepancies](hindsight-doc-code-discrepancies.md) — Catalogue of places where Hindsight READMEs, docs and comments disagree with the code or each other, with verification status and how to treat each.
- [Hindsight extensions, memory defense and webhooks](hindsight-extensions-defense-webhooks.md) — Hindsight's server extension slots, bundled extensions, the opt-in memory defense secret/PII filter, and signed webhook delivery.
- [Hindsight integrations and agent skills](hindsight-integrations.md) — The ~48 Hindsight integration packages grouped by integration mechanic, the LiteLLM wrapper, and the five agent skills shipped in the repo.
- [Hindsight LLM, embedding and reranker providers](hindsight-llm-embedding-providers.md) — Which LLM, embedding and reranker providers Hindsight supports, their defaults, and the provider abstraction in code.
- [Hindsight memory banks](hindsight-memory-banks.md) — Banks as isolated memory stores, with disposition traits, directives, aliases, templates, multilingual behaviour and export/import.
- [Hindsight overview](hindsight-overview.md) — What Vectorize's Hindsight agent-memory system is, how its monorepo is laid out, and where each subsystem is documented in this wiki.
- [Hindsight recall pipeline](hindsight-recall-pipeline.md) — How Hindsight retrieves memories with four parallel strategies, reciprocal rank fusion, reranking, boosts and token budgeting, with default parameters.
- [Hindsight reflect agent](hindsight-reflect-agent.md) — The agentic reflect operation: its tool loop, hierarchical retrieval order, disposition traits, directives and structured output.
- [Hindsight retain pipeline](hindsight-retain-pipeline.md) — How Hindsight turns input content into extracted facts, entities and graph links, including chunking, extraction modes, delta retain and attachments.
- [Hindsight storage and configuration](hindsight-storage-and-configuration.md) — Hindsight's PostgreSQL/Oracle storage, vector and text-search extensions, schema, and the hierarchical HINDSIGHT_API_* configuration system with key defaults.

## Agent memory — hy pages (compiled by a concurrent ingest)

- [Hy Memory and MemHub overview](hy-memory-overview.md) — Entry-point map of the Tencent Hunyuan Hy-Memory monorepo — the hy-memory Python SDK (chat, working, coding scenes) and the MemHub local-first product built on it.
- [Hy Memory chat hierarchy (L0–L7) and System 1 write path](hy-memory-chat-hierarchy-and-write-path.md) — The eight-layer chat memory model, the System 1 extract→reconcile→store write chain, multi-speaker ownership rules, and prompt-language handling.
- [Hy Memory chat retrieval pipeline and graph rerank](hy-memory-chat-retrieval-pipeline.md) — How chat search works — readers, multi-channel recall, additive BM25/tag fusion with RRF, schema and intention lanes, rerank, return channels, and graph projection and rerank.
- [Hy Memory coding version-evolution diff chain](hy-memory-coding-diff-chain.md) — The zero-LLM SQLite decorator that records every revision of a code block and attaches the revision history under retrieved coding facts.
- [Hy Memory plugins — OpenClaw and Hermes](hy-memory-plugins-openclaw-hermes.md) — How the OpenClaw TypeScript plugin and the Hermes Python memory provider integrate with Hy Memory, including tools, scope, auto recall/capture, managed mode, and known drifts.
- [Hy Memory releases, CI, dependencies, tests and security policy](hy-memory-release-ci-and-quality.md) — Version history highlights, CI and release workflows, dependency extras, test coverage areas, and security reporting policy for the Hy-Memory repo.
- [Hy Memory runtime, concurrency and observability](hy-memory-runtime-concurrency-and-observability.md) — How the SDK schedules work (write/search loops, SharedRuntime, workload gates, embedding batching) and what it logs, traces and measures.
- [Hy Memory SDK API, config and HTTP server](hy-memory-sdk-api-and-config.md) — Public surface of the hy-memory SDK — HyMemoryClient methods, modes, env-driven MemoryConfig keys, the stdlib HTTP server routes, and input constraints.
- [Hy Memory storage backends, snapshot and re-embedding](hy-memory-storage-and-reembed.md) — Vector, graph, cache and history store abstractions in the SDK, plus offline data-plane snapshot/restore and the re-embedding workflow.
- [Hy Memory System 2 evolution and cross-domain sweeper](hy-memory-system2-evolution.md) — Ultra-mode System 2 — explicit evolve() cycles that cluster facts, induce graph schemas with one LLM call per batch, and a cross-domain sweeper for core schemas.
- [Hy Memory working and coding scenes (two-layer memory)](hy-memory-working-coding-memory.md) — The facts + experiences memory used for working and coding scenes — schema, write and search flow, scene routing, workspace/branch isolation, and reconciliation rules.

## Agent memory — Mem0

- [Mem0 clients, CLI and integrations](mem0-clients-and-integrations.md) — Hosted and OSS client surfaces, CLI configuration, coding-agent plugins, and integration boundaries.
- [Mem0 OSS retrieval and ranking](mem0-retrieval.md) — Semantic candidate generation, optional BM25 and entity boosts, threshold behavior, expiration, and graph boundaries in Mem0 OSS.
- [Mem0 OSS write and storage](mem0-write-and-storage.md) — Additive extraction, deduplication, session history, vector payloads, entity indexing, and write-path limitations in Mem0 OSS.
- [Mem0 overview](mem0-overview.md) — Mem0's open-source memory SDK, self-hosted server, managed platform, and the boundaries between their capabilities.
- [Mem0 provider architecture](mem0-providers.md) — Factory-based LLM, embedding, vector-store, and reranking adapters and their optional capability boundaries.
- [Mem0 reported benchmarks and evaluation limits](mem0-benchmarks.md) — Vendor-reported managed-platform memory benchmark scores, conflicting published figures, and unavailable evaluation code.
- [Mem0 self-hosted server and security](mem0-server-and-security.md) — Self-hosted deployment topology, authentication, authorization boundaries, configuration, and important operational risks.
- [Mem0 source map and documentation discrepancies](mem0-source-map.md) — Coverage ledger, inspection limits, and consequential documentation conflicts for the Mem0 repository snapshot.

## Agent memory — TencentDB Agent Memory

- [TencentDB Agent Memory overview](tencentdb-agent-memory-overview.md) — Product architecture, memory asset model, and reported benchmark of TencentDB Agent Memory.
- [TencentDB Agent Memory source coverage map](tencentdb-source-map.md) — Revision, inspection ledger, exclusions, and outstanding coverage for the TencentDB Agent Memory repository.
- [TencentDB knowledge service and wiki ingestion](tencentdb-knowledge-service.md) — Wiki and CodeGraph ingestion, indexing, incremental updates, and agent tool access in MemoryKnowledge.
- [TencentDB memory layers and write pipeline](tencentdb-memory-pipeline.md) — L0 conversation capture and asynchronous L1, L2 and L3 memory synthesis in TencentDB MemoryCore.
- [TencentDB memory retrieval and storage](tencentdb-retrieval-storage.md) — MemoryCore search strategies, storage abstractions, backend differences, and isolation caveats.
- [TencentDB proxy, capture, and agent integrations](tencentdb-proxy-integrations.md) — Proxy turn processing, on-demand memory tools, capture, bridges, and SDK version boundaries.
- [TencentDB security and deployment boundaries](tencentdb-security-deployment.md) — Authentication, authorization, credential handling and deployment caveats across the TencentDB memory services.

## Note-taking — Memos

- [Memos access and privacy model](memos-security.md) — Memo audiences, sharing, authentication and security boundaries in Memos.
- [Memos API and MCP interfaces](memos-interfaces.md) — Structured API routing, live events and the OpenAPI-derived MCP adapter in Memos.
- [Memos data and storage](memos-data-and-storage.md) — Memo content, derived Markdown payloads and attachment persistence in Memos.
- [Memos deployment and configuration](memos-deployment.md) — Deployment defaults, declarative configuration and migration requirements for Memos.
- [Memos overview and architecture](memos-overview.md) — Product purpose and layered architecture of the self-hosted Memos note-taking application.
- [Memos source map and coverage](memos-source-map.md) — Source identity, inspection coverage, exclusions and outstanding limits for the Memos repository snapshot.

## Agent memory — memhub pages (compiled by a concurrent ingest)

- [MemHub apps, packages, CLI, i18n and release tooling](memhub-apps-and-packages.md) — Workspace layout of MemHub — CLI, Electron desktop, React web UI, site, shared TypeScript packages, runtime-control, i18n, and release/signing scripts.
- [MemHub embedding-space switching](memhub-embedding-space-switching.md) — How MemHub safely changes embedding models — space identity, 409 refusal with plan, full re-embed with rollback, retention, and the built-in local ONNX embedder.
- [MemHub host bridge and per-harness integration](memhub-host-bridge-harness-integration.md) — How MemHub installs MCP, hooks and skills into AI harnesses (Claude Code, Cursor, Codex, OpenCode, Qwen Code, Pi, Hermes, OpenClaw, WorkBuddy, DeepSeek) and the mechanics and risks of each.
- [MemHub memory modes, durable write queue and nightly evolve](memhub-memory-modes-and-write-queue.md) — How MemHub maps lite/pro/ultra onto SDK writes, schedules durable extraction jobs by event time with fairness rules, and runs nightly System 2 evolve.
- [MemHub privacy boundaries and permission model](memhub-privacy-and-permissions.md) — What MemHub stores and sends, its four independent permissions, absence of per-memory ACLs, diagnostics and debug-logging risks, and credential handling.
- [MemHub product architecture and data plane](memhub-product-architecture.md) — MemHub's single-Runtime process model, SDK-vs-management data authorities, API surfaces, contracts catalog, and operational gotchas.
- [MemHub source adapters, import and live sync](memhub-import-adapters-and-live-sync.md) — The SourceAdapter protocol, registered host sources, cursor rules, polling-plus-watch live sync, hook capture handoff, and source authorization checks.
