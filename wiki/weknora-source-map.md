---
type: SourceMap
title: WeKnora source map and coverage
description: Snapshot identity, per-file coverage ledger, exclusions, evidence limits, and follow-up targets for the WeKnora repository ingest.
tags: [ml, weknora, source-map]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:11:38Z }
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a258
    title: WeKnora v0.8.3 repository snapshot
---

This is the reconciliation ledger for the WeKnora package, not a claim of exhaustive code comprehension. **Observed:** the snapshot contains 5,664 Git-tracked artifacts. **Ingest process (not a repository claim):** five read-only exploration subagents examined architecture/persistence/queues, parsing/retrieval/connectors, agents/wiki/sandboxes, deployment/security, and frontend/clients/integrations; the curator reconciled their findings and added memory, crypto/config, wiki transaction, license, and manifest checks. A sixth read-only semantic reviewer spot-checked consequential claims and prompted precision corrections. All concept pages remain draft because material implementation coverage is incomplete.[^weknora]

## Identity and ownership

- Canonical entry: [README](../raw/WeKnora/README.md); package scope: `raw/WeKnora/`.
- Upstream identity: Tencent/WeKnora, as linked by the README; version file: `0.8.3`.
- Revision: `fd7a258`, commit subject “fix(docparser): escape standalone image filenames in Markdown (#4475),” author timestamp 2026-10-26.
- **Observed snapshot caveat:** the sole tracked worktree difference at inspection was a pre-existing `.gitignore` addition for `.pi/`. It was left unchanged. The ledger hashes local artifact bytes, so the revision is qualified by that explicit difference.
- WeKnora's own code is MIT. Third-party component terms remain separate; the top-level notice describes MPL source/notice bundles, Apache-licensed dictionary/OCR material, and other component notices. Detailed license texts and packaged source archives were not audited.[^weknora]

## Per-artifact coverage ledger

[The TSV inventory](weknora-source-inventory.tsv) contains one row per tracked artifact: package-relative path, local SHA-256, coverage state, and inspection/exclusion reason. Hashing is **not** semantic inspection or a privacy audit. The inventory was generated from `git ls-files -z`; tracked hidden manifests are included even where the source's ignore rules hide them from ordinary exploration.[^weknora]

| Coverage state | Artifacts | Meaning |
| --- | ---: | --- |
| `inspected-selected` | 230 | Static selected sections or symbol-level searches; does not promise a full-file audit |
| `test-intent-only` | 28 | Test names or selected source inspected; none executed |
| `excluded` | 386 | Vendored internals, detailed legal texts, generated contracts/bindings, lockfiles, translations, or visual assets, with per-file reasons |
| `pending` | 5,020 | Inventoried but not content-reviewed; no behavior attributed to them |
| **Total** | **5,664** | Tracked source closure at this snapshot |

The named inspected set is deliberately conservative: directory listings and test-suite counts do not promote every file in those directories to inspected. Inspection depth varies, including symbol-only searches. Source-dependent claims use precise locators in their concept footnotes; those claims must not be generalized to an entire pending subtree.[^weknora]

## Coverage by knowledge boundary

| Source family | Compiled destination | Principal remaining work |
| --- | --- | --- |
| `cmd/`, container/runtime/router, `go.mod` | [Architecture](weknora-backend-architecture.md) | Full provider composition, platform lifecycle, extension runtime behavior |
| Types, representative repositories, initial migration | [Persistence](weknora-persistence.md) | Later PostgreSQL/SQLite migrations, constraints and all tenant predicates |
| Task definitions/router/executor | [Queues](weknora-task-queues.md) | Handler idempotence, housekeeping, restart/load tests |
| Python facade/registry/config; Go chunker framework | [Ingestion](weknora-document-ingestion.md) | Format parser bodies, AnyDoc/MinerU/OCR/VLM converters, complete ingestion lifecycle |
| Fusion/rerank/composite/factory, selected PG/Milvus | [Retrieval](weknora-hybrid-retrieval.md) | Other drivers, embedding/rerank providers, actual index compatibility |
| Connector interfaces/metadata; scheduler symbols | [Sync](weknora-datasource-sync.md) | Every provider's auth, fetch, attachments, cursor and deletion correctness |
| Graph service sections/image keep rules | [Graph/images](weknora-graph-multimodal-retrieval.md) | Graph extraction/Cypher, image pipeline and multimodal provider quality |
| Agent engine/constants/capability map | [Agent](weknora-agent-runtime.md) | Act/observe, approvals/HITL/collaboration, compaction bodies |
| Skill manager/session sandbox contract | [Skills/sandboxes](weknora-skills-sandboxes.md) | Remote/local adapter enforcement, installs, network and lifecycle races |
| Wiki constants/extraction sections/page service/repository | [Wiki compilation](weknora-wiki-compilation.md) | Full map/reduce/finalize, cancellations, link consistency, graph UI |
| Memory types/recall/search/scheduling sections | [Memory](weknora-memory.md) | Repository scope, ranking/consolidation, confirmation/redaction/deletion tests |
| Frontend transport/state/build manifests | [Frontend](weknora-frontend-streaming.md) | Views, browser rendering, security and event-replay tests |
| CLI root/streams/credential interfaces; SDK streams | [CLI/SDK](weknora-cli-sdk.md) | Command CRUD, complete precedence matrix, acceptance tests |
| Endpoint/catalog/auth; Python transport sections | [MCP](weknora-mcp-servers.md) | Every tool handler; outbound MCP client/OAuth; protocol tests |
| Embed/widget/IM contracts/plugin sections | [Channels](weknora-publishing-channels.md) | Adapter signature bodies, embed policy/exchange, browser bridge and live integrations |
| Compose/chart/config/middleware/crypto selections | [Deployment](weknora-deployment.md), [configuration](weknora-configuration.md), [security](weknora-security.md) | Full templates/CI, OIDC, storage URL guards, all authorization and egress paths |

## Exclusions, attachments, and unavailable evidence

- `.git/` is VCS storage rather than product evidence; only revision/status/diff metadata were used. Ignored `.pi/` is local agent tooling and was not compiled. No other product worktree additions were reported by the inspected Git status.
- Translated READMEs duplicate the chosen English entry point. Lockfiles and generated protobuf/Swagger/Wails bindings are inventoried but excluded from synthesis in favor of source manifests/contracts. Vendored code is not treated as first-party architecture.
- Branding/screenshots/icons and appearance-only assets are excluded; no visual quality claims are made. The architecture SVG's **source text and paths** were inspected, not rendered. Other architecture figures remain outside the evidence used here.
- The README's externally hosted demo video, websites, release pages, model weights, remote dependencies, proprietary-provider APIs, packaged component source archives, and downloads were not fetched. Local release/docs trees, scripts, examples, datasets and fixtures not explicitly inspected remain **pending**, not silently counted as covered.
- Benchmark/recall/BLEU/ROUGE support is README-reported; no evaluation protocol, hardware, dataset result, uncertainty, or performance measurement was established. Such results cannot be inferred from test names or feature labels.[^weknora]

## Contradictions and drift

- **Reported current documentation drift:** the README Overview/feature table says 29 model vendors, while its historical v0.8.2 note says 27 and the architecture SVG still labels 27. The historical difference can reflect a release boundary; the SVG/current-table mismatch remains unresolved because the implementation catalog was not counted. Neither count is promoted to a verified v0.8.3 catalog size.[^weknora]
- Initial PostgreSQL parse-status default versus current code constants is unresolved; see [persistence](weknora-persistence.md). Later migration effects were not checked.
- Compose and Helm declare different ParadeDB versions; this is a deployment difference, not a reproduced incompatibility. Historical local-sandbox and MCP-version statements need edition/artifact qualification, as recorded in their concepts.

## Evidence and idempotency

**Observed** denotes static source inspection; **Reported** denotes documentation or comment assertions; **Synthesis** denotes explicit cross-file inference. No upstream behavior is labeled Reproduced or independently verified. Operational recipes and tests were not executed. Secret-shaped values seen in templates/fixtures were identified as examples rather than likely live credentials; no sensitive values were copied. This screening is limited to inspected inputs.[^weknora]

Future ingests should match normalized package scope plus revision, reconcile artifact hashes/states, and extend the existing concepts rather than creating one source per supporting file. This first ingest is **partial coverage**, so it does not justify a blanket no-op for every future request against the same revision. Complete already-compiled subtopics should remain unchanged unless evidence or useful relationships change.

## Relationships

- Documents the evidence boundary for [WeKnora](weknora.md) and every linked concept above.
- Uses the TSV as supporting canonical coverage data, not as an additional source identity.

[^weknora]: Snapshot `fd7a258`: [README](../raw/WeKnora/README.md), “Overview,” “Architecture,” “Features,” “Clients and Integrations,” and “Development”; `VERSION`; `LICENSE`, opening MIT terms; `THIRD_PARTY_NOTICES.md`, introduction and component sections; `docs/images/readme/architecture-en-light.svg`, services/model-catalog labels; `.gitignore` final addition. Repository metadata inspected with `git rev-parse HEAD`, `git log -1`, `git status --short --ignored`, `git diff -- .gitignore`, and `git ls-files -z`. Per-file methods and local hashes are persisted in [the coverage inventory](weknora-source-inventory.tsv); behavior-specific symbol locators appear in the linked concept footnotes.
