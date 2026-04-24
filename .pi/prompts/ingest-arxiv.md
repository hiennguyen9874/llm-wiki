---
description: Ingest an arXiv paper into the second brain
---

Read `AGENTS.md`. Activate `llm-wiki-core`, `llm-wiki-ingest`, `read-arxiv-paper`, `qmd`, and `obsidian-markdown`.

Treat $ARGUMENTS as an arXiv URL. Use `read-arxiv-paper` to normalize to `/src/`, download/reuse the cached source bundle, unpack it, and read from source files rather than PDF when possible. Preserve the raw paper source under `raw/papers/` with a stable arXiv-ID-based name and keep the original arXiv URL in source metadata. Do not write the skill's default `./knowledge/summary_*.md`; continue with the normal Ingest Workflow in `llm-wiki-ingest`.
