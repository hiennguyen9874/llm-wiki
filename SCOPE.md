# Knowledge Base Scope

Instance configuration under the base contract [`AGENTS.md`](AGENTS.md). Initialize or re-scope it with the `wiki-init` skill.

## Identity

- **Name:** Jev & Decision Models KB
- **Purpose:** Track Jev, the System One decision-model category, and its open and commercial alternatives (Kev, Laya, OpenJev variants, Clef, Julia, Von, and others): their architectures, decision APIs (Choice, Noul, Score), calibration, serving, benchmarks, field reception, and the agent and application patterns built on them.
- **Inclusion test:** a source or question is in scope when it yields durable knowledge about (a) Jev or a Jev-compatible or Jev-like typed-decision model, service, or tool; (b) the classifier, calibration, or evaluation methods needed to understand, compare, or choose them; or (c) agent, routing, memory, or context-management systems that use or are directly compared with such models.
- **Exclusions:** general LLM news, unrelated model releases, and agent tooling with no decision-model link; promotional claims without technical content; material the human marks as off-limits. Model weights and binaries in `raw/` are kept as evidence but never transcribed into the wiki.

## Domains

Domains emerge from ingested knowledge. Register a domain when it recurs across several concepts, needs its own rules, or selects domain tooling.

| Domain | Focus | Course profile | Rules |
| --- | --- | --- | --- |
| `decision-models` | Jev and Jev-compatible typed-decision models: architecture, APIs, serving, checkpoints, and comparisons | `ml` | Label vendor and model-card benchmarks **Reported** unless independently reproduced; record benchmark version, dataset, and comparator. Use `stale_after` for model releases, API shapes, pricing, and leaderboard figures. Disambiguate colliding names (OpenJev, CLM) in the concept body. |
| `calibration` | Probability calibration, thresholds, and evaluation methodology for classifiers and decision models | `ml` | State calibration method, fitted parameters, and the data split they were fitted on. |
| `agents` | Agent, routing, memory, compaction, and browser systems that use decision models | `ml` | Use `stale_after` for harness integrations and plugin APIs. |
| `community` | Field reports, critiques, prior-art claims, and reception threads | `general` | Treat claims as **Reported**; record disputes under `## Contradictions` without picking a side unless evidence resolves it. |

- Name domains as the human does; they may be broad (`health`) or narrow (`home-network`).
- A concept belongs to its primary domain through tags and, once groups exist, its group path.
- Domain rules cover things like citation style, verification expectations, or staleness windows.
- An unregistered domain uses the defaults below.

## Conventions

| Setting | Value |
| --- | --- |
| Default interaction mode | `autonomous` |
| Concept prose language | English; keep technical terms and model names in their original form. |
| Course prose language | Vietnamese, with technical keywords in English and an English gloss on first use. |
| Default course profile | `general` |

Course profiles live in `.pi/skills/wiki-learn/references/profiles/`. A domain without a matching profile uses `general`.

## Governance

- Registering a new domain or course-profile mapping needs no approval; record it here in the same change as the first affected concept.
- Narrowing scope, adding exclusions, or adding domain rules that change meaning, governance, or human control requires human approval, as defined in the base contract's contract evolution section.
