---
description: Ingest a batch of documents from raw/ sequentially
---

Activate:
- `llm-wiki-core`
- `llm-wiki-ingest`
- `llm-wiki-schema`
- `llm-wiki-governance`
- `llm-wiki-ops`
- `qmd`
- `obsidian-markdown`

Process unprocessed files from: $ARGUMENTS
Use the **Batch Ingest Workflow** in `llm-wiki-ingest`.

Process sequentially unless parallelism is clearly safe and explicitly approved. Ask before high-level taxonomy or irreversible structural decisions.
