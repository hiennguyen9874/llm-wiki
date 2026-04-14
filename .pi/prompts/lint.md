---
description: Run lint/full health check on wiki/
---

"Run a full health check on wiki/ per the lint workflow in AGENTS.md. Use QMD to find duplicates, orphans, stale pages, weak cross-links, under-integrated source pages, low-confidence knowledge, and unresolved supersession chains. Also check whether Bases and Canvases are out of sync with the markdown wiki. Auto-fix only safe issues such as obvious broken links or missing backlinks when unambiguous, and report the rest. Output to outputs/reports/lint-report-[date].md with severity levels (🔴 errors, 🟡 warnings, 🔵 info). Suggest 3 articles or sources to fill the biggest knowledge gaps."