---
description: Scan notes and artifacts for sensitive information handling issues
---

"Read AGENTS.md. Then activate `llm-wiki-core`, `llm-wiki-maintenance`, `qmd`, and `obsidian-markdown`. Scan $ARGUMENTS or recent downstream artifacts if no scope is given for secrets, credentials, tokens, PII, or other private material that should not have been promoted into `wiki/` or broadly reusable outputs. Redact downstream summaries only when the fix is safe and unambiguous, otherwise report the issue and ask the user before destructive handling. Record meaningful remediation in `wiki/log.md`."