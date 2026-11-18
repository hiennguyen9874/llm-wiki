---
type: Concept
title: Anthropic context management in Pydantic AI
description: How a Claude agent in Pydantic AI stays inside its context window — advisory task budgets and their client-side countdown, server-side and on-demand compaction with the parameters each drops, per-platform compaction support, token counting that may omit server tools, and the summed usage a server-side tool loop reports.
tags: [pydantic-ai, anthropic, context, compaction, cost]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:22:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-anthropic-2026
    resource: ../raw/models/anthropic/index.md
    scope: ../raw/models/anthropic/
    kind: documentation
    revision: sha256:4d8450abe7abd2367f5b9e163764ca396b66cadaf87d31aa5c1b5f08ca03a3ca
    title: "Anthropic"
---

A long Claude agent has four separate counters, and confusing them is the operational mistake this page exists to prevent: a **task budget** the model paces itself against, a **compaction threshold** the server acts on, a **token count** that may omit the tools that dominate the request, and a **usage figure** that sums every server-side tool round rather than describing the context the model saw.[^pydantic-anthropic-2026] All four are Anthropic-specific surfaces configured through `AnthropicModelSettings`, a capability or a model method, and all four sit on top of the route described in [Anthropic models in Pydantic AI](anthropic-models-in-pydantic-ai.md).

## Task budgets: an advisory countdown for a whole loop

Task budgets give Claude an advisory token budget for a full agentic loop — thinking, tool calls, tool results and output included — so the model can pace itself and finish gracefully as the budget is consumed rather than being cut off mid-loop[^pydantic-anthropic-2026] `AnthropicModelSettings.anthropic_task_budget` takes an `AnthropicTaskBudget` payload that maps to `output_config.task_budget`:

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel, AnthropicModelSettings

model = AnthropicModel('claude-opus-4-8')
settings = AnthropicModelSettings(
    anthropic_task_budget={'type': 'tokens', 'total': 20_000},
)
agent = Agent(model, model_settings=settings)
```

Pydantic AI enables Anthropic's required `task-budgets-2026-03-13` beta automatically when the setting is present[^pydantic-anthropic-2026] It is a beta with a model list: Anthropic's feature-support page holds the current one, task budgets are not documented as supported on Bedrock or Vertex, and on Microsoft Foundry the check is Microsoft's Claude capability list[^pydantic-anthropic-2026]

Budgets compose with `anthropic_effort`, which tunes per-step reasoning depth while the budget caps total work across the loop; both fields end up under the same `output_config` object[^pydantic-anthropic-2026]

**`remaining` is a client-side-compaction field.** The server tracks the countdown itself under server-side compaction, so with `AnthropicCompaction` the advice is to leave `remaining` unset and let `total` self-regulate[^pydantic-anthropic-2026] `remaining` exists for the pattern where *you* summarize earlier turns between requests and the server therefore has no memory of what was spent before the rewrite; Pydantic AI does not track it for you, so the value has to be accumulated yourself — from `RunUsage` on each run, for example — and passed on the next request so the countdown continues from where it left off instead of resetting to `total`[^pydantic-anthropic-2026] The cost of getting it wrong is not only budget accuracy: setting `remaining` invalidates any prompt-cache prefix that contains the budget, so preserving caching means setting `total` once and letting the server self-regulate[^pydantic-anthropic-2026]

## Server-side compaction

Anthropic can compact automatically: when input tokens exceed a configured threshold, the API generates a summary that replaces older messages while preserving context[^pydantic-anthropic-2026] After compaction, subsequent requests send only the compacted window, from the latest compaction block onward, which reduces request size even though the API ignores the earlier content either way[^pydantic-anthropic-2026] The standing system prompt is unaffected, because it travels in the separate `system` parameter that compaction does not replace[^pydantic-anthropic-2026]

The capability form is `AnthropicCompaction`:

| Argument | Meaning |
| --- | --- |
| `token_threshold` | Compaction triggers when input tokens exceed this; default 150,000, minimum 50,000 |
| `instructions` | Custom instructions for how the summary is generated |
| `pause_after_compaction` | When `True`, the response stops after the compaction block with `stop_reason='compaction'`, so the application can act before continuing |

The equivalent through model settings is a `compact_20260112` edit under `anthropic_context_management`:

```python
model_settings=AnthropicModelSettings(
    anthropic_context_management={
        'edits': [{'type': 'compact_20260112', 'trigger': {'type': 'input_tokens', 'value': 100_000}}]
    }
)
```

### On-demand compaction

To decide the moment yourself, call `AnthropicModel.compact_messages(...)`. It sends the conversation with Anthropic's on-demand compaction parameter, which summarizes instead of replying, and returns a `ModelResponse` holding one `CompactionPart` — a readable summary, with its signature in `provider_details` — which you then append to the history; later requests send it in place of the messages before it[^pydantic-anthropic-2026]

`instructions` is an optional focus for the summary, and the replacement is total: Anthropic replaces its whole summarization prompt with whatever instructions it is given, so Pydantic AI sends the focus inside a full summarization prompt of its own[^pydantic-anthropic-2026] The compaction request is the conversation's own request plus the `compaction` parameter, which is why it can read the conversation's prompt cache — provided the `ModelRequestContext` carries the same settings and request parameters, tools and output type included; the one a `before_model_request` hook receives does, while the hand-built one in the documented example matches only an agent with no tools, no structured output and no settings[^pydantic-anthropic-2026]

Anthropic rejects some parameters on a compaction request, and Pydantic AI leaves them out: `stop_sequences`, the structured output format, the `remaining` task budget and `anthropic_context_management`[^pydantic-anthropic-2026] A forcing `tool_choice` is relaxed to `auto`, and the tool calls of a trailing response that has no tool results yet are dropped[^pydantic-anthropic-2026] Images and documents in the summarized messages do not survive compaction[^pydantic-anthropic-2026]

Three accounting details follow from the response shape. Its usage is the compaction's, reported in `usage.iterations` rather than the top-level counts[^pydantic-anthropic-2026] The context it leaves behind, as `ctx.context_window_used` reads it, is the summary alone[^pydantic-anthropic-2026] And if Anthropic returns no summary — because `max_tokens` cut it off, for instance — Pydantic AI raises `UnexpectedModelBehavior` rather than returning an empty part[^pydantic-anthropic-2026]

Requests carrying a compaction block send the `compact-2026-09-04` beta, and do not get the default threshold compaction edit, which Anthropic rejects alongside it[^pydantic-anthropic-2026] For the same reason on-demand compaction must not be combined with `AnthropicCompaction` or with a `compact_20260112` edit of your own in one conversation: Anthropic rejects every request carrying both[^pydantic-anthropic-2026]

The block is portable across models that support on-demand compaction — Claude Fable 5 and 5.1, Mythos 5, 5.1 and Preview, Opus 4.6 and later, Sonnet 4.6 and later, and Haiku 5.5[^pydantic-anthropic-2026] `compact_messages` raises a `UserError` on any other model, per the `anthropic_supports_on_demand_compaction` profile flag[^pydantic-anthropic-2026]

### Support by transport is not the same as documentation

The source distinguishes two claims it keeps apart: "documented" means Anthropic's on-demand compaction docs list the platform, and "verified" means both a compaction request and a request sending the block back succeed there[^pydantic-anthropic-2026]

| Platform | Client | Support |
| --- | --- | --- |
| Claude API | `AsyncAnthropic` | Documented and verified |
| Claude Platform on AWS | `AsyncAnthropicAWS` | Documented, not verified by Pydantic AI |
| Bedrock Messages API | `AsyncAnthropicBedrockMantle` | Not documented, verified |
| Bedrock `InvokeModel` (legacy) | `AsyncAnthropicBedrock` | Not documented, verified |
| Google Cloud Vertex AI | `AsyncAnthropicVertex` | Documented, not verified by Pydantic AI |
| Microsoft Foundry | `AsyncAnthropicFoundry` | Documented, not verified by Pydantic AI |

Bedrock also serves fewer models than the Claude API — its Messages API does not serve Claude Haiku 5.5 or Sonnet 4.6, for example — so a model that supports on-demand compaction on the Claude API can be absent there[^pydantic-anthropic-2026]

## Token counting, and the tools it may omit

`count_tokens()` and `UsageLimits.count_tokens_before_request` use Anthropic's token-counting endpoint, and what that endpoint counts depends on the client[^pydantic-anthropic-2026] On the `AsyncAnthropic` client the count includes the definitions of the web search, web fetch, code execution, tool search and advisor tools, so it matches the request's input tokens[^pydantic-anthropic-2026] The Bedrock, Vertex AI and Foundry clients leave those tools out, because their count endpoints have not been verified to accept them, and **no** client counts MCP servers, which the endpoint rejects[^pydantic-anthropic-2026]

The `anthropic_count_tokens_accepts_server_tools` profile flag controls that. Set it to `False` when your `AsyncAnthropic` client's `base_url` points at a proxy whose count endpoint rejects server tools, or to `True` on a platform client whose endpoint accepts them[^pydantic-anthropic-2026] With it off, a request whose function tools are all deferred cannot be counted at all[^pydantic-anthropic-2026]

## Why one response's usage can exceed its context

A server-side tool — [web search](anthropic-server-side-tools.md), for instance — lets Anthropic sample the model several times within one request, once per tool round[^pydantic-anthropic-2026] The response's usage sums every pass, which is what Anthropic bills, but each pass re-reads the conversation so far, so the sum can be several times the context the model was given[^pydantic-anthropic-2026] A response in which compaction ran likewise sums the compaction pass and the pass after it, which saw only the compacted context[^pydantic-anthropic-2026]

Anthropic reports each pass only under a beta that returns `usage.iterations`[^pydantic-anthropic-2026] With it, `ctx.context_window_used`, `per_request_input_tokens_limit` and Harness compaction measure the context by the last pass's input tokens, cached tokens included; without it, all three read the summed usage[^pydantic-anthropic-2026] `AnthropicCompaction` and `anthropic_context_management` send the `compact-2026-01-12` beta, and the betas that `AdvisorTool` and `anthropic_task_budget` send return `usage.iterations` too; otherwise the beta has to be sent by hand with `anthropic_betas=['compact-2026-01-12']`[^pydantic-anthropic-2026] The response's usage and cost stay the sum of the passes either way[^pydantic-anthropic-2026]

## Limits

- The page names **no Pydantic AI version** and no date, so the settings, beta ids and thresholds here are version-unknown; the page is `draft` under the `pydantic-ai` domain rule[^pydantic-anthropic-2026]
- Evidence class is **Reported**: no key, model, compaction request or batch was used, so no summary was produced, no threshold triggered, no token count compared and no usage figure measured[^pydantic-anthropic-2026]
- The supported-model lists for task budgets and on-demand compaction are Anthropic's or Microsoft's, read as links rather than followed, and Betas move faster than a wiki page[^pydantic-anthropic-2026]
- The transport table's "verified" cells are the vendor's statement that both requests succeeded, not a test reproduced here[^pydantic-anthropic-2026]
- Anthropic's compaction summary quality, its cost against a hand-written summarizer and its effect on answer quality are not addressed by the source at all[^pydantic-anthropic-2026]

## Relationships

- **Configured through** the model settings and transports in [Anthropic models in Pydantic AI](anthropic-models-in-pydantic-ai.md), whose client choice decides which compaction platforms are reachable.
- **Compacts history that** [Anthropic prompt caching](anthropic-prompt-caching.md) has cached: the `remaining` field and the compaction block both interact with cached prefixes, and the `compact_20260112` beta is what produces `usage.iterations`.
- **Counts against** the run budgets and limits in [run controls](pydantic-ai-run-controls.md), where `count_tokens_before_request` and `per_request_input_tokens_limit` are defined.
- **Feeds** [observability](pydantic-ai-observability.md) and Harness compaction with its context measurement, and is the Anthropic analogue of the OpenAI compaction recorded in [OpenAI Responses API features](openai-responses-api-features.md).
- **Server-side tool passes** counted here are issued by the tools in [Anthropic server-side tools](anthropic-server-side-tools.md), whose callers decide whether code execution runs at all.
- **Mitigates** the `ModelContextWindowExceededError` that [model API errors](pydantic-ai-model-api-errors.md) records, and the Harness-side equivalent in [Pydantic AI Harness](pydantic-ai-harness.md).

[^pydantic-anthropic-2026]: Pydantic Docs, "Anthropic", <https://pydantic.dev/docs/ai/models/anthropic/>, 8,470 words as declared and 8,506 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/anthropic/index.md`, 995 lines, content digest sha256:4d8450ab. §"Task Budgets (Beta)" (raw lines 199–226) for the advisory loop budget, `anthropic_task_budget` → `output_config.task_budget`, the auto-enabled `task-budgets-2026-03-13` beta, the platform caveats, the composition with `anthropic_effort`, and the `remaining`-field rules including the cache invalidation and the `RunUsage` accumulation; §"Message Compaction" (775–819) for the server-side threshold, the compacted window, the untouched `system` parameter, `AnthropicCompaction`'s three arguments and the `compact_20260112` edit; "Compacting on demand" (820–872) for `compact_messages`, the `CompactionPart`, the rewritten summarization prompt, the shared-request and cache read, the dropped parameters, the relaxed `tool_choice`, the lost images and documents, `usage.iterations`, `context_window_used`, `UnexpectedModelBehavior`, the `compact-2026-09-04` beta, the double-compaction rejection, the model list and the `anthropic_supports_on_demand_compaction` flag; the six-row platform table and the Bedrock model gap at 826–872; §"Token counting" (571–576) for the endpoint, the server tools `AsyncAnthropic` counts, the platform omissions, MCP exclusion and `anthropic_count_tokens_accepts_server_tools`; §"Server-side tool loops" (873–896) for the per-pass re-read, the summed usage, the compaction-pass sum, the `usage.iterations` beta, the three consumers that measure by last pass, the betas that return it and the unchanged total. Evidence class: **Reported** — vendor documentation; nothing was compacted, counted or measured.
