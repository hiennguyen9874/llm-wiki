---
description: Run lint/full health check on wiki/
---

"Read AGENTS.md. Then activate `llm-wiki-core`, `llm-wiki-maintenance`, `qmd`, and `obsidian-markdown`. Run the full lint workflow from the maintenance skill on `wiki/`. Use QMD to find duplicates, orphans, stale pages, weak cross-links, under-integrated source pages, low-confidence knowledge, unresolved supersession chains, and Bases/Canvases that are out of sync with the markdown layer. Auto-fix only safe issues such as obvious broken links or missing backlinks when unambiguous, and report the rest. Output to `outputs/reports/lint-report-[date].md` with severity levels (🔴 errors, 🟡 warnings, 🔵 info), then suggest 3 important gaps, 3 next sources to ingest, and 3 pages or artifacts needing consolidation."
