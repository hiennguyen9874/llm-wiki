---
title: "Tool Search"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/capabilities/tool-search/"
domain: "pydantic.dev"
language: "en"
description: "Let the model discover deferred tools on demand with the Pydantic AI ToolSearch capability, so agents with many tools only pay tokens for the ones they use."
word_count: 213
---

The [`ToolSearch`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.ToolSearch) [capability](https://pydantic.dev/docs/ai/capabilities/overview/) handles model-driven discovery of searchable tools marked with `defer_loading=True`, so agents with large toolsets only pay tokens for the tools the model needs. Like the [provider-adaptive tools](https://pydantic.dev/docs/ai/capabilities/overview/#provider-adaptive-tools) above, it picks the best path for the active model — native server-executed search on Anthropic and OpenAI Responses, a local `search_tools` function tool elsewhere — and is auto-injected into every agent when searchable deferred tools exist. Bundle-level disclosure is covered by [on-demand capabilities](https://pydantic.dev/docs/ai/capabilities/on-demand/).

It declares a default `id` of `'tool_search'`, so two instances merge into one instead of raising a duplicate-id error — see [building custom capabilities](https://pydantic.dev/docs/ai/capabilities/custom/) for the merge rules.

Pass an explicit [`ToolSearch`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.ToolSearch) to pick a specific [`strategy`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.ToolSearch.strategy) (`'keywords'`, `'bm25'`, `'regex'`, or a custom callable) or tune the local fallback:

tool\_search\_capability.py

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import ToolSearch

agent = Agent('anthropic:claude-sonnet-5-5', capabilities=[ToolSearch(strategy='keywords')])
```

When the local `search_tools` function tool is used, its retry budget follows the agent’s tool budget — so `Agent(retries={'tools': N})` gives the model `N` attempts to correct a malformed `queries` argument, on the same [precedence ladder](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#which-retry-limit-wins) as any other tool. A search that finds no matches returns normally and never spends a retry.

See [Tool Search](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-search) for when to reach for it, the full strategy table, and provider support details.
