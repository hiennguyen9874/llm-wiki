# Knowledge Base Scope

Instance configuration under the base contract [`AGENTS.md`](AGENTS.md). Initialize or re-scope it with the `wiki-init` skill.

## Identity

- **Name:** Pydantic AI knowledge base
- **Purpose:** A working reference for building production LLM agents in Python with Pydantic AI v2 — the capability primitive, the Harness and its ecosystem packages, pydantic-graph, pydantic-evals, and the operational concerns (durability, observability, approvals, MCP, caching, sandboxing) that surround them. Sources are read to decide how to build and operate an agent, not to survey the framework market.
- **Inclusion test:** a source or question is in scope when it yields durable, attributable knowledge about Pydantic AI (its core, first-party packages, or the integrations it ships) or about an adjacent tool only insofar as a comparison positions Pydantic AI (for example LangChain, the OpenAI Agents SDK, MCP transports, durability backends). The subject must be reusable beyond one reading and answer a build, migration, or operating question.
- **Exclusions:** general machine-learning theory and model-architecture research that does not inform an agent build; other frameworks' internals unless the source compares them with Pydantic AI; vendor marketing and promotional blocks; anything the human marks off-limits.

## Domains

Domains emerge from ingested knowledge. Register a domain when it recurs across several concepts, needs its own rules, or selects domain tooling.

| Domain | Focus | Course profile | Rules |
| --- | --- | --- | --- |
| `pydantic-ai` | The Pydantic AI framework: the capability primitive, the Harness, release and migration guidance, and its ecosystem | `general` | Name the framework version (for example v2.59.0) next to any API, default, or behaviour claim, and mark it `draft` when only vendor material supports it. Keep vendor-authored and independent sources distinguishable in the citations. |
| `ml` | LLM and agent-architecture knowledge that outlives one framework release | `ml` | Use `stale_after` for framework APIs, model releases, and benchmarks. |

- Name domains as the human does; they may be broad (`health`) or narrow (`home-network`).
- A concept belongs to its primary domain through tags and, once groups exist, its group path.
- Domain rules cover things like citation style, verification expectations, or staleness windows.
- An unregistered domain uses the defaults below.

## Conventions

| Setting | Value |
| --- | --- |
| Default interaction mode | `autonomous` |
| Concept prose language | Match the human's request; keep technical terms in their original language. |
| Course prose language | Vietnamese, with technical keywords in English and an English gloss on first use. |
| Default course profile | `general` |

Course profiles live in `.pi/skills/wiki-learn/references/profiles/`. A domain without a matching profile uses `general`.

## Governance

- Registering a new domain or course-profile mapping needs no approval; record it here in the same change as the first affected concept.
- Narrowing scope, adding exclusions, or adding domain rules that change meaning, governance, or human control requires human approval, as defined in the base contract's contract evolution section.
