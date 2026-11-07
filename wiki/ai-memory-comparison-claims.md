---
type: Concept
title: ai-memory self-reported comparison with other agent-memory tools
description: What the ai-memory README and comparison doc claim relative to Mem0, Zep, basic-memory, Hindsight, Claude Code memory and others, labelled as self-reported and point-in-time.
tags: [ai-memory, comparison, agent-memory, self-reported]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
stale_after: 2027-01-06
sources:
  - id: readme
    resource: ../raw/ai-memory/README.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory README
  - id: comparison
    resource: ../raw/ai-memory/docs/comparison.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: How ai-memory compares
  - id: landscape
    resource: ../raw/ai-memory/docs/research-2026-landscape.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: 2026 landscape research
---

# ai-memory self-reported comparison with other agent-memory tools

The ai-memory repository positions itself against other memory tools in two places: a "Coming from another tool?" table in the README and `docs/comparison.md`.[^readme][^comparison] Everything here is **Reported by the project itself** — an advocacy document by the tool's author, not independent evaluation — and the competitor figures are a **point-in-time snapshot** (star counts dated 2026-10-18 per delegated reading).[^comparison]

Evidence class: **Reported** throughout; nothing was cross-checked against the other tools' sources, although several of those repositories (mem0, cognee, hindsight, memos, gbrain, …) exist elsewhere in this knowledge base's `raw/` folder.

## Claimed positioning

The comparison doc groups competitors by optimization target: atomic **facts** (Mem0, LangMem), temporal **knowledge graph** (Zep/Graphiti, Cognee), agent-editable **memory OS** (Letta, MemOS), **context database** (OpenViking), and **hook capture for coding agents** (claude-mem, MemPalace, agentmemory). ai-memory claims a different anchor: a git-backed markdown wiki as source of truth with a derived retrieval index, captured from lifecycle hooks, shared across agents and machines.[^comparison] It concedes that markdown-as-memory has become common among other tools.[^comparison]

| Coming from… | Claimed carry-over | Claimed gain |
| --- | --- | --- |
| Mem0 / fact extractors | automatic per-turn capture | editable pages instead of fact rows; no cloud key needed |
| Zep / Graphiti | temporal reasoning, typed relations | `as_of` and typed edges without a graph database |
| mcp-memory-service | SQLite, local embeddings, hook capture | pages, claim-once handoffs, zero-LLM reversible aging |
| basic-memory | markdown-on-disk | automatic capture, derived index, handoffs, multi-user |
| Claude Code built-in memory | zero-setup convenience | cross-machine/agent sync, search, team use |
| Hindsight / OpenViking | living pages, background consolidation | zero-LLM default; opt-in dream; markdown is the source of truth |
| Supermemory / LiquidLM | managed second brain | git-versioned files you own, offline |

Source: README table.[^readme]

## Caveats the project itself states

- The comparison page "claims no ranking": competitor retrieval benchmarks use incomparable harnesses; the project's own numbers are in [Evals and benchmarks](ai-memory-evals-and-benchmarks.md).[^comparison]
- A "where we're behind" section exists; `research-2026-landscape.md` is a refreshed 2026-10 analysis.[^comparison][^landscape]
- Proxy-asserted users bypass per-project grants (see [Auth and security](ai-memory-auth-and-security.md)), which tempers the "per-project multi-user auth" headline (synthesis).

## Relationships

- Overview: [ai-memory overview](ai-memory-overview.md).
- Per-tool claims about other systems should be checked against their own sources; this page does not independently verify them.

[^readme]: `../raw/ai-memory/README.md` — "Coming from another tool?" table and following paragraphs.
[^comparison]: `../raw/ai-memory/docs/comparison.md` — "The short version", camp groupings, maturity and "where we're behind" sections (delegated reading; snapshot date from that reading).
[^landscape]: `../raw/ai-memory/docs/research-2026-landscape.md` — head only (skimmed by delegate).
