# Knowledge Base Scope

Instance configuration under the base contract [`AGENTS.md`](AGENTS.md). Initialize or re-scope it with the `wiki-init` skill.

## Identity

- **Name:** Embedding & Retrieval Models KB
- **Purpose:** Track, compare, and choose embedding, reranking, and late-interaction retrieval models (text, code, multimodal, visual-document), their architectures, training methods, and benchmarks, to support model selection for retrieval/RAG systems.
- **Inclusion test:** a source or question is in scope when it yields durable knowledge about a retrieval model, its backbone encoder, its training/alignment method, or a retrieval benchmark or leaderboard.
- **Exclusions:** general-purpose LLM/chat models without a retrieval role; vector databases and serving infrastructure, unless the source ties them to a specific model; marketing material with no technical substance; material the human marks as off-limits.

## Domains

Domains emerge from ingested knowledge. Register a domain when it recurs across several concepts, needs its own rules, or selects domain tooling.

| Domain | Focus | Course profile | Rules |
| --- | --- | --- | --- |
| `embedding` | Dense, sparse, multi-vector, and multimodal embedding models and their backbones | `ml` | Record params, backbone, pooling, dims/Matryoshka, context, license, languages; label vendor scores as Reported (self-reported). |
| `reranking` | Cross-encoder, listwise, and multimodal rerankers and context pruners | `ml` | Record scoring mode (pointwise/listwise), context limit, license; scope benchmark comparisons to one protocol. |
| `benchmarks` | MTEB/MMTEB, RTEB, MMEB, ViDoRe, and leaderboard snapshots | `ml` | Store snapshot date and benchmark version; set `stale_after` (≈90 days) on rankings; never mix scores across benchmark versions. |

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
