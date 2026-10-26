---
type: Concept
title: Pydantic AI run controls
description: Provider-neutral model error categories, run and request time budgets, append-only instructions, and the warnings Pydantic AI raises when a model ignores a setting.
tags: [ml, pydantic-ai, agents, reliability]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T04:07:00Z }
stale_after: 2026-12-23
sources:
  - id: dd-v2-tour-2026
    resource: ../raw/pydantic-ai-whats-new-2026/index.md
    scope: ../raw/pydantic-ai-whats-new-2026/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP"
---

v2.58.0 and v2.59.0 (2026-10-19 and 2026-10-20) turned two hand-rolled pieces of production plumbing into framework features: classifying model failures the same way across providers, and bounding a run with real time budgets. Both are small API surfaces with large operational effect[^dd-v2-tour-2026]

## Provider-neutral error categories

v2.59.0 added `ModelRateLimitError`, `ModelUnavailableError`, `ModelServerError` and `ModelContextWindowExceededError`, plus `ModelQuotaExceededError`, so a 429 is caught the same way whether it came from OpenAI, Anthropic or Bedrock. `ModelHTTPError.for_category(...)` builds an error of a given category[^dd-v2-tour-2026]

Two properties make this a migration-friendly change rather than a replacement:

- The category error stays a `ModelHTTPError`, so existing `except ModelHTTPError` handlers keep working. The author's run printed `isinstance(err, ModelHTTPError) == True` for a `ModelRateLimitError` built by `for_category`[^dd-v2-tour-2026]
- The categories are what a durability layer classifies on: `TemporalDurability` gained `non_retryable_model_errors` so a context-window overflow that can never succeed stops being retried[^dd-v2-tour-2026]

```python
try:
    agent.run_sync('Summarize the release notes.', timeout=60.0)
except ModelRateLimitError as err:
    print('rate limited, back off:', type(err).__name__)
except (ModelUnavailableError, ModelContextWindowExceededError) as err:
    print('switch model or trim context:', type(err).__name__)
```

## Time budgets at two scopes

| Setting | Scope | Covers |
| --- | --- | --- |
| `timeout=` on a run | The whole agent run | All steps, tool calls and model requests |
| `RunContext.deadline` | The run, readable inside tools and hooks | The same budget, visible to code |
| `ModelSettings['request_timeout']` | One model request | All attempts and stream consumption of that request |
| `ModelSettings['max_retries']` | Provider SDK retries | How many times the provider SDK retries |

When a model ignores a setting such as `timeout`, `max_retries` or `stop_sequences`, the framework now raises `UnsupportedSettingWarning`, which turns silent no-ops into visible ones[^dd-v2-tour-2026]

## Append-only instructions

`on_change='append'` on an instruction function adds its changes to the end of the prompt instead of rewriting the prefix, so a value that changes between turns stops breaking the [prompt cache](pydantic-ai-prompt-caching.md). Two conditions apply: the function must be named (`@agent.instructions(name='style', on_change='append')`), because without `name=` the mode emits a `UserWarning` and falls back to rewriting the prefix; and the pasted value must be genuinely append-safe, since it now sits after everything else the capability contributed[^dd-v2-tour-2026]

## Compatibility details worth a changelog read

- Omitted provider usage is now distinguished from a reported zero, with a `UsageLimitUnavailableWarning`[^dd-v2-tour-2026]
- A resumed `'suspended'` response's usage counts only in the run that produced it.
- `read_file` can return images and PDFs.
- The shut-down Groq models `playai-tts`, `playai-tts-arabic`, `meta-llama/llama-guard-4-12b` and `meta-llama/llama-4-maverick-17b-128e-instruct` were removed.

## Construction-time failure

In 2.57.0, `Agent('anthropic:claude-sonnet-5-5')` raised `UserError` when `ANTHROPIC_API_KEY` was unset — at construction, not at first run. Tests therefore need either placeholder keys in the environment or `TestModel`/`agent.override(model='test')`[^dd-v2-tour-2026] This is a deliberate fail-fast choice that changes how test fixtures are arranged.

## Limits

- The verified claims here come from the author's run against `pydantic-ai-slim` 2.59.0 with Pyright reporting zero errors; nothing was installed or executed in this ingest[^dd-v2-tour-2026]
- Deadline semantics under streaming, retries that straddle a deadline, and warning categories beyond those named are not documented in this capture.
- The security advisories shipped in the same releases are recorded in [Pydantic AI v2 release](pydantic-ai-v2-release.md) rather than here, and one v2.59.0 advisory is unnamed in the source.
- Evidence class: **Reported**.

## Relationships

- **Depends on** [Pydantic AI v2 release](pydantic-ai-v2-release.md) for the version history these settings arrived in.
- **Enables** [durable execution](pydantic-ai-durable-execution.md) retry policies through `non_retryable_model_errors`.
- **Protects** [prompt caching](pydantic-ai-prompt-caching.md) through append-only instructions.
- **Surfaced through** [observability](pydantic-ai-observability.md) warnings and spans.

[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"What changed in v2.58 and v2.59 (October 19-20)" (raw lines 21–76) for the error categories, `for_category`, `non_retryable_model_errors`, the run and request time budgets, `UnsupportedSettingWarning`, append-only instructions, and the compatibility bullets; §"Gotchas I hit while checking the examples" for construction-time API-key failure. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — the author type-checked and ran a 2.59.0 sample; this ingest executed nothing.
