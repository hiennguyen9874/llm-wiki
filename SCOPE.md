# Knowledge Base Scope

Instance configuration under the base contract [`AGENTS.md`](AGENTS.md). Initialize or re-scope it with the `wiki-init` skill.

## Identity

- **Name:** Looped Models KB
- **Purpose:** A research knowledge base on looped, recurrent-depth, and weight-tied transformers: architectures, training stability, scaling laws, adaptive computation and early exit, latent reasoning, inference and serving, and models built on them.
- **Inclusion test:** a source or question is in scope when it studies, builds, evaluates, or serves repeated application of shared layers or blocks (looped, recurrent-depth, universal, recursive, or layer-reuse transformers), or supplies context needed to interpret such work: untied-depth and MoE baselines, implicit and latent reasoning, systematic generalization, and training recipes used by a looped model.
- **Exclusions:** general LLM news and architectures with no looped or recurrent-depth connection; standalone agent, data-synthesis, or RL methods not tied to a looped model or comparison; material the human marks as off-limits.

## Domains

Domains emerge from ingested knowledge. Register a domain when it recurs across several concepts, needs its own rules, or selects domain tooling.

| Domain | Focus | Course profile | Rules |
| --- | --- | --- | --- |
| `looped-models` | Looped and recurrent-depth architectures, stability, scaling laws, adaptive depth and early exit, MoE interplay, inference and KV cache | `ml` | State the comparison basis (stored parameters, FLOPs, effective depth, KV cache, wall-clock) for every efficiency or quality claim; distinguish theoretical FLOP savings from measured speed. Use `stale_after` for model releases, benchmarks, and framework APIs. |
| `reasoning` | Implicit and latent reasoning, grokking, parametric memory, systematic and compositional generalization | `ml` | Name the task family (synthetic vs natural benchmark) a result comes from; do not generalize synthetic findings without labeling them synthesis. |
| `agent-training` | Post-training and data recipes used by looped models (SFT, RL, trajectory synthesis) | `ml` | Link each concept to the looped model or study that uses it. |

- Name domains as the human does; they may be broad (`health`) or narrow (`home-network`).
- A concept belongs to its primary domain through tags and, once groups exist, its group path.
- Domain rules cover things like citation style, verification expectations, or staleness windows.
- Secondary or rumor reports about unreleased models stay `draft` with claims labeled `Reported` or `Unverified`.
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
