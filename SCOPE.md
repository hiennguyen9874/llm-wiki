# Knowledge Base Scope

Instance configuration under the base contract [`AGENTS.md`](AGENTS.md). Initialize or re-scope it with the `wiki-init` skill.

## Identity

- **Name:** Personal knowledge base
- **Purpose:** A general-purpose personal knowledge base. It is not bound to one subject; any domain the human curates is eligible.
- **Inclusion test:** a source or question is in scope when the human supplies or requests it and it yields durable knowledge. Any subject qualifies.
- **Exclusions:** material the human marks as off-limits.

## Domains

Domains emerge from ingested knowledge. Register a domain when it recurs across several concepts, needs its own rules, or selects domain tooling.

| Domain | Focus | Course profile | Rules |
| --- | --- | --- | --- |
| eta | Eta personal agent desktop, Bot, mobile companion, and shared core | general | — |
| foreman | Foreman coding-agent supervision, evidence, routing, and integrations | general | — |
| pi-agents | Pi Agents extension, delegation, messaging, and configuration | general | — |
| pi-durable | Durable agent harness: Pi Durable concepts and deployment patterns | general | — |
| pi-orbs | Pi Orbs bots, Sprite deployment, integrations, and security | general | — |
| pi-pocket | Pi Pocket application, operation, security, and orchestration | general | — |
| pi-tab | Pi Tab browser agent, execution modes, recovery, and security | general | — |

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
