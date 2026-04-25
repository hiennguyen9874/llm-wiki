---
title: Review Queue
created: 2026-04-24
last_updated: 2026-04-24
status: active
page_type: procedure
tags: [outputs, review]
visibility: private
---

# Review Queue

One markdown note per human judgment item. Use for non-blocking decisions raised during ingest, query, maintenance, crystallization, or graph-insights-lite.

Recommended frontmatter for each item:

```yaml
---
title: Review - Short Decision
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
status: open
page_type: review_item
action_type: approve_edit
priority: medium
source: []
related_pages: []
visibility: private
---
```

Allowed `action_type`: `approve_edit`, `create_page`, `deep_research`, `skip`, `ask_user`, `resolve_contradiction`.
