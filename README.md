# LLM Wiki

Personal second brain. Agent does the knowledge work; human steers direction.

> **Mission:** Turn raw material into durable, compounding memory. Compile once, update with evidence, reuse later.

## Structure

| Layer | Purpose |
|---|---|
| `raw/` | Immutable capture (sources, web clips, papers) |
| `wiki/` | Durable semantic knowledge |
| `wiki/bases/` | Operational dashboards |
| `wiki/canvases/` | Visual synthesis |
| `outputs/` | Derived analyses, briefings, crystallizations |

## Workflows

```
New material → raw/ → Ingest → wiki/ → outputs/
Question     → Query → Answer → (save if durable)
Session end  → Crystallize → wiki/ + outputs/
Health check → Maintenance → wiki/ + log
```

See [`AGENTS.md`](./AGENTS.md) for the full skill-activation routing table.

## Prompts

Prompts are thin entry points in [`.pi/prompts/`](./.pi/prompts/). Real policy lives in skills.

### Ingest
| Prompt | When to use |
|---|---|
| `ingest.md` | Source already in `raw/` |
| `ingest-url.md` | Start from a web URL |
| `ingest-arxiv.md` | Start from an arXiv URL |
| `ingest-pdf.md` | Start from a PDF |
| `ingest-batch.md` | Process a queue of unprocessed files |

### Query & Synthesis
| Prompt | When to use |
|---|---|
| `query.md` | Answer a question from the vault |
| `brief.md` | Short, decision-oriented summary |
| `briefing.md` | Fuller executive-style synthesis |
| `connections.md` | Find meaningful links between topics |
| `disagreements.md` | Surface conflicting claims |
| `gaps.md` | Find missing or underdeveloped knowledge |
| `explore.md` | Discover latent connections in the vault |
| `next-research.md` | Recommend what to research next |
| `deep-research.md` | Deep investigation on a topic |

### Maintenance & Review
| Prompt | When to use |
|---|---|
| `review.md` | Weekly/monthly operational pass |
| `lint.md` | Structured health audit |
| `retention-pass.md` | Stale-knowledge / decay review |
| `resolve-contradictions.md` | Targeted conflict resolution |
| `privacy-scan.md` | Sensitive-content audit |
| `compile.md` | Compile raw sources into canonical wiki pages |

### Session
| Prompt | When to use |
|---|---|
| `session-start.md` | Load context at start of session |
| `session-end.md` | Distill session into episodic memory |
| `crystallize.md` | Promote finished research into durable memory |

## Skills

Skills define the actual workflow policy in [`.pi/skills/`](./.pi/skills/).

| Skill | Role |
|---|---|
| [`llm-wiki-core`](./.pi/skills/llm-wiki-core/SKILL.md) | Base OS: architecture, lifecycle, naming, provenance rules |
| [`llm-wiki-schema`](./.pi/skills/llm-wiki-schema/SKILL.md) | Frontmatter, note structure, page-shape rules |
| [`llm-wiki-governance`](./.pi/skills/llm-wiki-governance/SKILL.md) | Privacy, contradiction/supersession, risky-change policy |
| [`llm-wiki-ops`](./.pi/skills/llm-wiki-ops/SKILL.md) | Naming, layout, index/log, catalog operations |
| [`llm-wiki-ingest`](./.pi/skills/llm-wiki-ingest/SKILL.md) | Processing new source material |
| [`llm-wiki-query`](./.pi/skills/llm-wiki-query/SKILL.md) | Retrieval, Q&A, briefings, gap scans |
| [`llm-wiki-crystallize`](./.pi/skills/llm-wiki-crystallize/SKILL.md) | Turn sessions into durable memory |
| [`llm-wiki-maintenance`](./.pi/skills/llm-wiki-maintenance/SKILL.md) | Review, lint, retention, health checks |
| [`llm-wiki-visualization`](./.pi/skills/llm-wiki-visualization/SKILL.md) | Canvases, Bases, live vault validation |

Companion tools: `qmd` (search), `obsidian-markdown`, `defuddle` (web cleaning), `json-canvas`, `obsidian-bases`, `obsidian-cli`, `ask-user`.

## Setup

```sh
npm install -g @mariozechner/pi-coding-agent
npm install -g @tobilu/qmd
# + Obsidian
```

## Key Rules

- Preserve raw sources — never mutate `raw/`
- Prefer updating existing pages over creating duplicates
- Cite factual claims; preserve uncertainty explicitly
- Update `wiki/index.md` and append to `wiki/log.md` after meaningful changes
- Ask before bulk renames, deletions, or taxonomy/schema changes

## Extending

- Global rules → `AGENTS.md`
- User-facing entry points → `.pi/prompts/`
- Workflow policy → `.pi/skills/`
- Local hooks/guardrails → `.pi/extensions/` (see [`docs/pi-hooks-local.md`](./docs/pi-hooks-local.md))

## References

- [LLM Wiki (Karpathy)](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [LLM Wiki v2](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2)

## TODO
- QMD use more better
