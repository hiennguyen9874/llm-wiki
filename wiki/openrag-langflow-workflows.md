---
type: Concept
title: "OpenRAG Langflow workflow bundle"
description: "The four committed Langflow flows, create-only provisioning, runtime tweaks, component synchronization, and customization constraints."
tags: [ml, openrag, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:56:21Z }
stale_after: 2027-01-24
sources:
  - id: openrag-repo
    resource: ../raw/openrag/README.md
    scope: ../raw/openrag/
    kind: code
    revision: 6fc819d3ec10
    title: OpenRAG repository
---

**Observed:** four committed Langflow JSON flows implement chat, nudges, file ingestion, and URL ingestion. The backend provisions missing flows, preserves existing flow edits, and passes runtime configuration through tweaks and global-variable headers; running a template directly in Langflow is not necessarily equivalent to running it through OpenRAG.[^openrag-repo]

## Flow inventory

| Artifact | Role | Nodes | Committed lock |
| --- | --- | --- | --- |
| `flows/openrag_agent.json` | Agent chat with retrieval and tool calls | 11 | Locked |
| `flows/openrag_nudges.json` | Contextual prompt suggestions | 8 | Locked |
| `flows/ingestion_flow.json` | Docling file parsing/chunking/indexing path | 8 | Unlocked |
| `flows/openrag_url_mcp.json` | URL ingestion exposed to the agent as a Langflow MCP tool | 9 | Locked |

Flow IDs are configured in backend settings. `ensure_flows_exist` creates on a 404 and does not overwrite an existing flow; other unexpected responses do not justify replacement. The URL flow is MCP-enabled and provisioning configures its Langflow project MCP auth to `none`. This internal Langflow MCP surface is distinct from OpenRAG's API-key-protected public `/mcp` server.[^openrag-repo]

## Component and credential wiring

Custom OpenRAG LLM and embedding components speak the backend's OpenAI-compatible proxy using `OPENRAG_LLM_BASE_URL`, `OPENRAG_LLM_TOKEN`, and selected-model variables. Backend runtime injection also supplies document identity, ACLs, parser options, callback URL/token, and filter expressions. The Langflow container loads `/app/custom_components`; image defaults disable arbitrary custom-component authoring and code-interpreter components.[^openrag-repo]

Flow JSON also embeds component source code. **Synthesis:** repository Python files and serialized component bodies are distinct synchronization surfaces; simply editing one Python file does not establish that all persisted user flows use it. Embedded copies were inventoried, not audited line-for-line for equivalence.[^openrag-repo]

## Supported editing and destructive restore

**Reported documentation:** local custom code requires `LANGFLOW_ALLOW_CUSTOM_COMPONENTS=true`; SaaS does not support custom component code. Use the recommended OpenRAG model components and do not assume adding custom metadata to the OpenSearch component is supported. Unlock, save, edit, save, then test through OpenRAG; the Langflow Playground lacks required runtime values. Start a new conversation after agent edits.[^openrag-repo]

Restore for Agent/Knowledge Ingestion discards customizations. Other flows need an exported backup or reset/reinstallation. **Observed discrepancy:** generic unlock instructions do not match the ingestion template's committed unlocked state. Documentation's eight-component agent screenshot/text also describes an older/simpler topology than the current eleven-node JSON; the screenshot was visually inspected, not treated as the live flow.[^openrag-repo]

## Relationships

- Implements [ingestion](openrag-document-ingestion.md), [retrieval](openrag-hybrid-retrieval.md), and [chat/nudges](openrag-chat-streaming.md).
- Depends on [deployment](openrag-deployment.md) for flow assets and [security](openrag-auth-security.md) for token boundaries.
- Distinct from the public [MCP server](openrag-mcp.md).

## Coverage limits

Flow node/edge/template inspection does not execute the graph or prove every embedded code copy matches source. Runtime backups and persisted user edits were not available; see [source map](openrag-source-map.md).

[^openrag-repo]: `6fc819d3ec10`: `flows/{openrag_agent,openrag_nudges,ingestion_flow,openrag_url_mcp}.json::data.nodes/data.edges/locked`; `src/config/settings.py` flow-ID constants; `src/services/flows_service.py::{ensure_flows_exist,_lock_flow,enable_mcp_none_for_url_ingest_flow}`; `src/utils/langflow_headers.py`; `custom_components/openrag/{openai_compatible_llm,openai_compatible_embedding}.py`; `Dockerfile.langflow::LANGFLOW_COMPONENTS_PATH/LANGFLOW_ALLOW_CUSTOM_COMPONENTS/LANGFLOW_BLOCK_CODE_INTERPRETER_COMPONENTS`; `docs/docs/core-components/{agents,editing-in-langflow,chat}.mdx`; `docs/static/img/opensearch-agent-flow.png` full graph.
