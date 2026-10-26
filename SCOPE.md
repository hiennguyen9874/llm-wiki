# Knowledge Base Scope

Instance configuration under the base contract [`AGENTS.md`](AGENTS.md). Initialize or re-scope it with the `wiki-init` skill.

## Identity

- **Name:** Open-source RAG platform engineering
- **Purpose:** Compile and compare how open-source retrieval-augmented generation platforms are built, operated, and secured, from pinned repository snapshots and their documentation.
- **Inclusion test:** a source or question is in scope when it concerns one of the tracked platforms (OpenRAG, RAGFlow, RAG-Anything, UltraRAG, WeKnora), another open-source RAG or agentic-retrieval system worth comparing, or a cross-cutting concern of those systems — architecture, parsing and ingestion, retrieval and ranking, agent workflows, knowledge compilation, persistence, deployment, integrations, or security — and yields durable, code-grounded knowledge.
- **Exclusions:** off-topic personal material; general ML theory or software topics that do not inform RAG platform engineering; vendor marketing claims kept as claims only, never as measured capability; material the human marks as off-limits.

## Domains

Domains emerge from ingested knowledge. Register a domain when it recurs across several concepts, needs its own rules, or selects domain tooling.

| Domain | Focus | Course profile | Rules |
| --- | --- | --- | --- |
| `rag` | Platform architecture, parsing and ingestion, hybrid retrieval and ranking, agent workflows, knowledge compilation | `general` | Ground claims in a pinned revision; label evidence as Observed, Reported, or Synthesis; keep unread coverage visible. |
| `operations` | Build, deployment, configuration, persistence, task queues, testing and validation of the tracked platforms | `general` | Set `stale_after` for version-specific build, deployment, and configuration guidance. |
| `security` | Authentication, authorization, connector and MCP boundaries, credential and disclosure limits | `general` | Redact sensitive values and record what a static review could not establish. |
| `ml` | Model and retrieval-model internals the platforms depend on | `ml` | Use `stale_after` for framework APIs, model releases, and benchmarks. |

- Name domains as the human does; they may be broad (`health`) or narrow (`home-network`).
- A concept belongs to its primary domain through tags and, once groups exist, its group path.
- Domain rules cover things like citation style, verification expectations, or staleness windows.
- An unregistered domain uses the defaults below.

## Conventions

| Setting | Value |
| --- | --- |
| Default interaction mode | `autonomous` |
| Concept prose language | English, with technical terms kept in their original form. |
| Course prose language | Vietnamese, with technical keywords in English and an English gloss on first use. |
| Default course profile | `general` |
| Source pinning | Each platform is a read-only `raw/<platform>/` snapshot; every concept cites its `resource`, `scope`, and inspected `revision`. |

Course profiles live in `.pi/skills/wiki-learn/references/profiles/`. A domain without a matching profile uses `general`.

## Governance

- Registering a new domain or course-profile mapping needs no approval; record it here in the same change as the first affected concept.
- Narrowing scope, adding exclusions, or adding domain rules that change meaning, governance, or human control requires human approval, as defined in the base contract's contract evolution section.
