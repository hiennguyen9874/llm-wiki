---
description: Run a lint and full health check across the wiki
---

Activate:
- `llm-wiki-core`
- `llm-wiki-maintenance`
- `llm-wiki-governance`
- `llm-wiki-ops`
- `llm-wiki-schema`
- `qmd`
- `obsidian-markdown`

Run the **Lint Workflow** in `llm-wiki-maintenance` on `wiki/`.
Save the report to `outputs/reports/lint-report-[date].md`.
Use the repo's safe-repair boundary; ask before risky merges, taxonomy changes, or deletions.
