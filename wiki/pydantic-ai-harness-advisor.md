---
type: Concept
title: Pydantic AI Harness advisor
description: The Harness Advisor capability — one consultation tool that runs provider-native on Anthropic or OpenRouter and as a separate advisor agent everywhere else, with its per-request budget, what each path forwards, how advisors merge, and where local execution breaks under durability.
tags: [pydantic-ai, agents, harness, tools]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:52:38Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-advisor-docs
    resource: ../raw/harness/advisor/index.md
    scope: ../raw/harness/advisor/
    kind: documentation
    revision: sha256:4b1c1efc23fdc4ab509bf58fc79e31b5f225104e898e41502cd1bd5849308bd5
    title: "Advisor"
---

`Advisor` is the [Harness](pydantic-ai-harness.md) capability that lets an executor model consult a second, often stronger model mid-run instead of committing to an answer unaided[^pydantic-advisor-docs] It exposes one *logical* tool through the same two-path shape as core's provider-adaptive tools: a provider-native advisor tool when executor and advisor sit on a compatible Anthropic or OpenRouter pairing, and otherwise a local `advisor` function tool that runs a separate Pydantic AI agent with the advisor model[^pydantic-advisor-docs] The interesting design point is which path wins by default. The [native-or-local](pydantic-ai-native-or-local-capabilities.md) switch in core matches a service to a provider; here the second half is a *model*, so native selection stays conservative and the local fallback is the universal path.

## Use

The advisor model is the first argument and accepts anything an `Agent` accepts as a model — a name such as `'anthropic:claude-opus-5-5'` or a `Model` instance[^pydantic-advisor-docs] The executor decides when to consult: nothing forces a call unless the user prompt or the agent's instructions ask for one, so a required consultation is a prompting decision, not a capability setting[^pydantic-advisor-docs]

```python
from pydantic_ai import Agent
from pydantic_ai_harness import Advisor

agent = Agent(
    'openai:gpt-6.1-sol',
    capabilities=[
        Advisor('anthropic:claude-opus-5-5', max_uses=1, max_tokens=4096)
    ],
)
result = agent.run_sync('Design a zero-downtime database migration. Consult the advisor before choosing a plan.')
```

## Which path runs

Native selection is deliberately narrow[^pydantic-advisor-docs]:

- **Native** needs both models on a compatible Anthropic provider, or both on OpenRouter, and the executor's model profile must support the advisor tool.
- **Local fallback** is every other pairing: an `advisor` function tool whose call runs a separate Pydantic AI agent.

By default the capability reuses only an explicit provider-qualified model name when executor and advisor share a provider, so it will not guess how an Anthropic model ID maps to an OpenRouter catalog slug — `Advisor('anthropic:claude-opus-5-5')` is native under an Anthropic executor and local everywhere else, while `Advisor('openrouter:anthropic/claude-opus-4.8')` is native under an OpenRouter executor[^pydantic-advisor-docs]

Three consequences follow[^pydantic-advisor-docs]:

| Input | Effect on the path |
| --- | --- |
| A `Model` instance | Always runs locally, keeping its own provider, client, credentials, base URL and instrumentation |
| A model name | Resolved only when a consultation runs locally; a native consultation therefore uses the executor provider's configuration |
| A renamed provider subclass, e.g. an `AnthropicProvider` subclass called `claude-code` | Counts as the provider it extends; it does not fall back when the executor lacks support |

`local=False` keeps the consultation inside the executor provider; `native=False` forces a separate request to the configured advisor provider[^pydantic-advisor-docs] With the built native advisor, `local=False` requires an `anthropic:<model>` or `openrouter:<model>` string and an executor on that same provider, while a `native=` replacement carries its own model.

## Options

| Option | Default | Behaviour |
| --- | --- | --- |
| `model` | required | Advisor model name or `Model` instance |
| `native` | `True` | The provider-native advisor; `False` disables it, an `AdvisorTool` instance or a function returning one replaces it and ignores the fields |
| `local` | `True` | The local fallback; `True` builds the `advisor` tool, `False` disables it, a `Tool` or function replaces it and keeps its own tool name |
| `output_type` | `str` | Local advisor output specification; a non-default value requires local execution |
| `max_uses` | `None` | Maximum consultations in one executor model request (int ≥ 1, or a callable of `RunContext`) |
| `max_tokens` | `None` | Maximum output tokens per consultation; values below 1024 are rejected so the option stays valid on every path |
| `caching` | `None` | Native-only prompt-cache TTL, `'5m'` or `'1h'`; Anthropic supports it, OpenRouter and the local path have no equivalent |
| `forward_history` | `False` | Forward completed executor message history to local consultations |
| `id` | `'advisor'` | Capability and toolset ID; advisors sharing it merge into one |
| `defer_loading` | `False` | Makes `Advisor` an [on-demand capability](pydantic-ai-on-demand-capabilities.md) loaded by `id` |
| `description` | `None` | Catalog text the model reads to decide whether to load an on-demand `Advisor` |

A `local=` replacement cannot be combined with `output_type`, `forward_history=True`, or — on OpenRouter — `max_uses`, because those only shape the built tool; `max_uses`, `max_tokens` and `caching` still shape the native advisor[^pydantic-advisor-docs] Invalid combinations fail when `Advisor` is constructed or when a merge produces one, and executor-versus-provider compatibility is checked when a run prepares its model request[^pydantic-advisor-docs]

The deprecated `mode` option still works until pydantic-ai-harness 1.0 with a `HarnessDeprecationWarning`: `'native'` equals `local=False`, `'local'` equals `native=False`, and `'auto'` is the default[^pydantic-advisor-docs] Combining `mode` with a non-default `native` or `local` raises `UserError`.

## Budget

`max_uses` has the per-request scope of Anthropic's native tool and resets on the next request[^pydantic-advisor-docs] On the local path a call counts once its arguments validate, even if the consultation then fails; parallel calls cannot exceed the cap; without `max_uses`, the run's usage limits bound local consultations within one request.

A callable `max_uses` receives the `RunContext` and returns that request's limit, which is how a budget shared across runs lives in `deps` — `max_uses=lambda ctx: 5 - ctx.deps.consulted`[^pydantic-advisor-docs] The native tool is sent with that limit; the local tool reads it once per request when the tool is prepared. Below `1`, the native tool is omitted from the request and the local tool stays visible but returns its limit message. Because the callable is Python (like `output_type`) and runs for every request — inside workflow code under durable execution — it should be cheap and deterministic.

OpenRouter's native tool ignores `max_uses` and applies its own fixed per-request limit, so by default setting `max_uses` with an OpenRouter advisor selects the local fallback; `local=False` with the built native advisor raises `ValueError`[^pydantic-advisor-docs]

## What the advisor sees

The context depends on the path, and that difference is the practical portability cost[^pydantic-advisor-docs]:

| Path | Advisor context |
| --- | --- |
| Anthropic native | The provider supplies the full transcript: system instructions, tool definitions, earlier turns and results, and executor text produced so far |
| OpenRouter native | The executor supplies a consultation prompt; Pydantic AI configures `forward_transcript=false` |
| Local fallback | The executor supplies a consultation prompt through the `advisor` tool; with `forward_history=True` the advisor also receives the executor's completed message history |

The local advisor has its own instructions and no access to the executor's dependencies, tools or toolsets, so for portable behaviour the executor must put the question and all relevant evidence into the consultation prompt — which the local tool description asks for[^pydantic-advisor-docs] `forward_history` does not change native-versus-local selection, and the current response — partial text and unresolved tool calls included — is never forwarded, so the prompt still needs the complete current question. Forwarded history arrives as structured message history, `system_prompt` parts and tool calls with results included.

## Structured answers

`output_type` takes the same output specification as an `Agent` — a Pydantic model, a scalar, `NativeOutput(...)` — and defaults to `str`; the advisor model must support the chosen output mode[^pydantic-advisor-docs] Successful consultations return the validated object as the tool result, and once `max_uses` is exhausted the tool returns a plain-text limit message instead.

Provider-native advisor tools accept no output schema, so a non-default `output_type` consults locally and combining it with `local=False` raises `ValueError`[^pydantic-advisor-docs] That constraint is what makes "native-only" and "typed advice" mutually exclusive.

## Usage, failures and tracing

Local advisor requests share the parent run's `RunUsage` and `UsageLimits`, so their requests and tokens count toward the agent tree's normal limits[^pydantic-advisor-docs] With `count_tokens_before_request=True`, a model that implements `count_tokens` has the consultation counted before sending; when the consultation raises `NotImplementedError` before any request is counted, it is retried once without the up-front count and the token and cost limits are checked against the response instead of failing the run — unless the shared usage has counted a request since the consultation started, as a concurrent sibling call would. A local advisor run is filed under the parent run's `conversation_id`, so it groups with the conversation it advises. Native usage arrives by provider protocol: Anthropic records advisor values in `RequestUsage.details`, OpenRouter exposes aggregate server-tool counts in response provider details.

Failure handling differs by path[^pydantic-advisor-docs]:

- Anthropic reports native advisor errors as tool results, so the executor continues.
- A local advisor that produces invalid model behaviour gives the executor a normal tool retry, matching other subagent-backed tools.
- Local model resolution, authentication, provider, request and usage-limit errors propagate and can stop the run.

`Advisor` emits no spans of its own[^pydantic-advisor-docs] With instrumentation enabled globally (`logfire.instrument_pydantic_ai()`), a local consultation appears as an agent run named `advisor`, and per-agent `instrument=` on the executor does not reach it; a native consultation is simply part of the executor's model request.

## Composition and merging

The tool is visible from the start unless `defer_loading=True` puts it on demand, and with `local=False` a request whose `max_uses` callable returns less than `1` carries no advisor tool at all[^pydantic-advisor-docs] Keep `id` stable once deployed, because loading and history replay key on it; the built tool is named `advisor` and the toolset ID defaults to `advisor`, so two advisors with different ids conflict over the tool name.

Two `Advisor` capabilities sharing an `id` merge like any native-or-local capability[^pydantic-advisor-docs] An option left at `None` (`max_uses`, `max_tokens`, `caching`) takes the other instance's value, two list `output_type`s are combined, and every other option takes the later instance's value. Since `native` and `local` both default to `True`, a later advisor left at its defaults restores the built native advisor and local tool, replacing an earlier `False` or replacement — the behaviour the default `mode='auto'` had. One merge that no single constructor accepts survives with a `UserWarning`: an OpenRouter advisor with `local=False` and the built native advisor carrying a `max_uses` drops the `max_uses` rather than failing the build.

## Streaming and durability

During streaming the executor stream pauses while a consultation runs and resumes when the completed advice is available; the local fallback does not splice advisor token deltas into the executor stream[^pydantic-advisor-docs]

Native advice stays part of the executor model request, so it is compatible with [durable execution](pydantic-ai-durable-execution.md)[^pydantic-advisor-docs] Local execution cannot yet preserve the same semantics across every backend: Temporal and Prefect can checkpoint the returned advice but do not merge the activity-local or task-local `RunUsage` changes back into the outer run, while [DBOS](pydantic-ai-dbos.md) checkpoints each local consultation so replay reuses the recorded advice. Under [Temporal](pydantic-ai-temporal.md) and Prefect, pass `local=False` with a supported provider; local execution there — including the default fallback — is unsupported. `Advisor` cannot detect a durable run, because Pydantic AI exposes no public durable-context contract, so it does not reject local execution inside one.

## Agent specs

String model configurations load from YAML or JSON agent specs when `Advisor` is passed in `custom_capability_types`[^pydantic-advisor-docs] `from_spec` names every JSON-expressible parameter — `model`, `native`, `local`, `max_uses`, `max_tokens`, `caching`, `forward_history`, `id`, `defer_loading`, `description` — because that signature generates the spec's JSON schema; `output_type` has no JSON form and passes through `**kwargs`, which the schema omits. Runtime `Model` instances and custom output specifications stay Python-only.

`__post_init__` validates the declared configuration and resolves `native` and `local` on construction and again on every merged or per-run copy, so a merge cannot reach a combination no constructor accepts[^pydantic-advisor-docs] `for_run` returns a fresh capability whose local usage is isolated to that run, because the `advisor` tool counts consultations on the capability it was built from, and `after_model_request` resets the local consultation allowance after each executor response.

## Limits

- The source is one vendor documentation page — "Advisor", Pydantic Docs, 3,131 words as declared and 3,199 by local `wc -w`, **no publication date, author, licence or Pydantic AI version**. It states only that the Harness is on 0.x and that minor releases may change the API, so under the `pydantic-ai` domain rule this page is `draft` and every API name is version-unknown[^pydantic-advisor-docs]
- Nothing was executed: no package installed, `Advisor` constructed, consultation sent, model resolved, merge performed, durable run replayed or trace inspected. Every behavioural claim is **Reported**[^pydantic-advisor-docs]
- The samples pin `openai:gpt-6.1-sol`, `anthropic:claude-opus-5-5` and `anthropic:claude-opus-4-8`, aliases no other capture here corroborates; that the advisor is "often stronger" is the vendor's framing, not a measured comparison.
- Unstated: what a native consultation costs relative to the separate request it replaces, whether the OpenRouter fixed limit has a documented number, the local tool's JSON schema and description text, how a native advisor failure is classified inside `RequestUsage.details`, and whether any harness release has shipped since the page was written.
- External links — the native `AdvisorTool` page, the capabilities overview's provider-adaptive section, on-demand loading, `RunUsage`/`UsageLimits`, `RunContext`, `combine` and the version policy — were read as links, not followed.

## Relationships

- **Is a** [Harness](pydantic-ai-harness.md) [capability](pydantic-ai-capability-primitive.md), listed as `Advisor` in the [capability catalog](pydantic-ai-capability-catalog.md) under reasoning, planning and delegation.
- **Extends** the [native-or-local](pydantic-ai-native-or-local-capabilities.md) pattern from a provider service to a second model, and inherits its `native=`/`local=` switch, merge rule and on-demand opt-in.
- **Uses** [on-demand loading](pydantic-ai-on-demand-capabilities.md) when `defer_loading=True`, which makes the `id` a load key rather than only a merge key.
- **Contrasts with** [Harness subagents](pydantic-ai-subagents.md): a delegate does work in its own run and returns a report, while an advisor is consulted for an answer inside the executor's request and cannot use the executor's tools.
- **Constrains** [durable execution](pydantic-ai-durable-execution.md) placement — native advice is request-local and safe, whereas local advice needs the provider-specific checkpointing described on [Pydantic AI on Temporal](pydantic-ai-temporal.md), [DBOS](pydantic-ai-dbos.md) and Prefect.
- **Shares the spec boundary with** [agent specs](pydantic-ai-agent-specs.md): `from_spec` exposes only the JSON-expressible fields, so a typed `output_type` stays in Python.
- **Depends on** the [message history](pydantic-ai-message-history.md) contract when `forward_history=True`, since forwarded messages are the structured history that page records.
- **Reports into** [observability](pydantic-ai-observability.md) only through global instrumentation — a local consultation is an `advisor` agent run, a native one is part of the executor's model request.

[^pydantic-advisor-docs]: Pydantic Docs, "Advisor", <https://pydantic.dev/docs/ai/harness/advisor/>; local capture `raw/harness/advisor/index.md`, content digest sha256:4b1c1efc, 3,131 words as declared (3,199 by `wc -w`), 424 lines, no publication date, author, licence or Pydantic AI version, with the Harness described as on 0.x. Lines 11–32 for the one-sentence purpose and the diagram (executor ↔ advisor tool, local advisor agent run with its own instructions and no access to your tools, provider-run `AdvisorTool`); lines 34–59 for the usage example and the executor-decides rule; lines 61–82 for `output_type`, the validated tool result, the limit message and the `local=False` `ValueError`; lines 84–103 for native-or-local selection, the conservative provider-qualified matching, the Anthropic/OpenRouter examples, `Model` instances running locally, name resolution at consultation time, the executor-profile requirement, and the renamed-subclass rule; lines 105–119 for the eleven-option table; lines 121–123 for `local=False`/`native=False` semantics and the deprecated `mode` mapping; lines 125–127 for the per-request `max_uses` scope, validation counting, parallel calls, usage-limit bounding, the callable form, the native limit and the below-1 behaviour; lines 129–133 for OpenRouter's ignored `max_uses`, the `ValueError`, `forward_history` not affecting selection, the un-forwarded current response and the agent-spec support; lines 135–147 for the three-row context table, the local advisor's isolation, and the forwarded structured history; lines 149–155 for shared usage and limits, `count_tokens_before_request`, the `NotImplementedError` retry, `conversation_id`, native usage reporting, construction- and prepare-time validation, the per-path failure handling, the limit message, no own spans, the global-instrumentation `advisor` run and the per-agent `instrument=` limit; lines 157–165 for start-visible versus on-demand, the no-tool request below 1, the stable `id`, the tool and toolset names, the merge rules, the restored defaults and the OpenRouter `max_uses` `UserWarning`; lines 157–165 also for streaming pause and the durability split (native safe, Temporal/Prefect usage not merged, DBOS replaying recorded advice, `local=False` under Temporal and Prefect, the missing durable-context contract); lines 167–423 for the API reference (`Advisor` bases, `id`, `model`, `output_type`, `max_uses`, `max_tokens`, `caching`, `forward_history`, `mode`, `__init__`, `from_spec`, `__post_init__`, `combine`, `for_run`, `after_model_request`). Evidence class: **Reported** — vendor documentation with no execution behind it.
