---
type: Concept
title: Pydantic AI instrumentation format
description: What Pydantic AI puts on the wire — the instrumentation format versions with v5 the default and 2–6 still selectable, the aggregated-usage attribute names on run spans, the three emitted histograms, and the three settings that redact content, binary data and request parameters.
tags: [pydantic-ai, observability, opentelemetry, privacy]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T12:05:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-logfire-docs
    resource: ../raw/integrations/logfire/index.md
    scope: ../raw/integrations/logfire/
    kind: documentation
    revision: sha256:5ea6a3e098a0dc8e4c1337ae9bebbef2d5489cc135597569711c1a96e77d6381
    title: "Pydantic Logfire Debugging and Monitoring"
---

Pydantic AI's instrumentation is a versioned wire contract rather than a single switch: the spans are shaped by a format version whose default is 5, four older versions remain selectable for pipelines that have not moved, and version 6 is opt-in because it changes which message role a tool result arrives under[^pydantic-logfire-docs] Beside the role decisions sit two independent concerns — attribute naming for usage, which decides whether a backend double-counts, and three settings that decide how much prompt, binary and schema detail leaves the process[^pydantic-logfire-docs] This page covers what the instrumentation emits; how to install it, choose a backend and instrument HTTP belongs to [Pydantic AI observability](pydantic-ai-observability.md), and the cache attributes have their own page in [prompt-cache health](pydantic-ai-prompt-cache-health.md).

## Format versions

The format follows version 1.37.0 of the OpenTelemetry Semantic Conventions for Generative AI systems and is selected with the `version` parameter of `InstrumentationSettings`; the default is `version=5`[^pydantic-logfire-docs] Versions 2, 3 and 4 are deprecated compatibility formats, and passing one emits a `PydanticAIDeprecationWarning` — the docs' advice is version 5 unless a telemetry pipeline is being preserved temporarily[^pydantic-logfire-docs]

| Version | What it settled | Status there now |
| --- | --- | --- |
| 2 | Instructions in `gen_ai.system_instructions`; `gen_ai.input.messages`/`gen_ai.output.messages` on model request spans; `pydantic_ai.all_messages` on agent run spans | Deprecated; some span and attribute names are not fully spec-compliant for compatibility reasons |
| 3 | Spec-compliant span names — `invoke_agent {gen_ai.agent.name}` and `execute_tool {gen_ai.tool.name}` — `tool_arguments` → `gen_ai.tool.call.arguments`, `tool_response` → `gen_ai.tool.call.result`, and thinking-token capture | Deprecated |
| 4 | Multimodal content: URL media as `{"type": "uri", "modality": …, "uri": …, "mime_type": …}` instead of `image-url`, inline bytes as `{"type": "blob", …}` instead of `binary` | Deprecated |
| 5 | `CallDeferred` and `ApprovalRequired` stop recording an exception event or setting span status ERROR; the span is left UNSET because a deferral is control flow | Default |
| 6 | Tool results move from a `tool_call_response` part inside a `{"role": "user"}` message to a `{"role": "tool"}` message, matching the GenAI conventions | Opt-in |

The v4 `modality` field appears only for image, audio and video content; `DocumentUrl` and unsupported media types omit it[^pydantic-logfire-docs] The v5 change is the one that makes a deferred approval readable as a decision rather than a failure, which is why the docs describe it as a semantic fix rather than a naming one[^pydantic-logfire-docs]

Version 6 is opt-in on the stated ground that it "changes the role of messages you already receive", so it should be passed explicitly once the consumer is ready[^pydantic-logfire-docs] Under it, `pydantic_ai.all_messages` keeps recording the stored history, while a model request span's `gen_ai.input.messages` records the history as sent — by then a `RetryFeedbackPart` has been translated into the prompt part its `retry.cause` calls for, so that attribute reads the same at every version[^pydantic-logfire-docs] The retry feedback that answers no tool call moves too: a `'no_output'` cause takes a `{"role": "system"}` message and `'validation_error'` or `'model_retry'` stay on the `{"role": "user"}` message they were already on[^pydantic-logfire-docs] A request whose parts span both roles is emitted as consecutive messages in part order rather than one merged message[^pydantic-logfire-docs]

**Synthesis:** the version number is therefore a deployment boundary with two directions — a consumer upgraded ahead of the emitter sees the new role and breaks, and an emitter left behind keeps a backend that aggregates by role silently wrong — which is why the docs recommend pinning it explicitly rather than waiting for a default change.

## Aggregated usage attributes

Model request spans use the standard `gen_ai.usage.input_tokens` and `gen_ai.usage.output_tokens`, while agent run spans use `gen_ai.aggregated_usage.input_tokens`, `gen_ai.aggregated_usage.output_tokens` and `gen_ai.aggregated_usage.details.*`[^pydantic-logfire-docs] The stated reason is that a run span reports the sum of its own request spans, so a backend that aggregates usage attributes across parent and child spans would count the same tokens twice[^pydantic-logfire-docs]

What a run span reports is what that run spent: a run that delegates to another agent does not include the delegate's tokens, whether or not the delegate is instrumented — if it is, its own run span reports them[^pydantic-logfire-docs] So the agent run spans in a trace can be added up as they are, and the total matches the sum of the `gen_ai.usage.*` attributes on the model request spans underneath them[^pydantic-logfire-docs]

A backend that wants the standard attribute on run spans instead turns aggregated names off and takes on the double-counting itself[^pydantic-logfire-docs]:

```python
from pydantic_ai import Agent
from pydantic_ai.models.instrumented import InstrumentationSettings

Agent.instrument_all(InstrumentationSettings(use_aggregated_usage_attribute_names=False))
```

## Emitted metrics

Instrumentation emits three metrics, all histograms[^pydantic-logfire-docs]:

| Metric | Unit | What it measures |
| --- | --- | --- |
| `gen_ai.client.token.usage` | `{token}` | Tokens per model or embedding request, split by the `gen_ai.token.type` attribute (`input` or `output`); defined by the GenAI semantic conventions |
| `operation.cost` | `{USD}` | Estimated cost of each model or embedding request, recorded when a price is known for the model |
| `gen_ai.client.operation.time_to_first_chunk` | `s` | Time from issuing a streaming request to the first chunk being surfaced; streaming requests only, and also set as a span attribute of the same name |

Each metric point carries `gen_ai.provider.name` (and the legacy `gen_ai.system`), `gen_ai.operation.name`, `gen_ai.request.model` and `gen_ai.response.model`, so a histogram can be broken down by provider and model[^pydantic-logfire-docs] Decision spans are the exception: they record no metrics because the model request span above them already reports the total of their usage[^pydantic-logfire-docs] See [Logfire decision tracing](logfire-decision-tracing.md) for that span's own attributes.

`operation.cost` and `{USD}` are also the meter behind [Pydantic AI cost and spend limits](pydantic-ai-cost-and-spend-limits.md), where the same estimate is a brake rather than a dashboard figure.

## Redacting content, binary data and schemas

Three `InstrumentationSettings` flags cut what leaves the process, and they compose[^pydantic-logfire-docs]:

| Setting | Removes | Leaves | Does not cover |
| --- | --- | --- | --- |
| `include_content=False` | User prompts, model completions, tool call arguments and responses, all other message content; exception messages and stack traces keep only the exception type | Structural information — spans, names, counts — and, on decision spans, question types and numbers | Run metadata, spans of your own, and request or response bodies captured by `instrument_httpx(capture_all=True)` |
| `include_binary_content=False` | Binary file data — images, audio, documents — from user prompts, model responses, tool returns, the agent's output, output-function arguments and run/tool deferral metadata | Media type everywhere; for a value recorded as a file, its vendor metadata and identifier, where the identifier is derived from the content if unset | Binary content held as a field of a model or dataclass you define, which is recorded in full |
| `include_model_request_parameters=False` | The per-request `model_request_parameters` attribute, which serializes the whole `ModelRequestParameters` including output configuration and every tool definition | `gen_ai.tool.definitions` — tool name, description and parameters — still emitted, so a platform that reads available tools from it is unaffected | Nothing else; the attribute is simply omitted |

The redaction is set the same two ways as any instrumentation setting — on the agent as an `Instrumentation` capability, or globally[^pydantic-logfire-docs]:

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import Instrumentation
from pydantic_ai.models.instrumented import InstrumentationSettings

agent = Agent('openai:gpt-6.1-sol', capabilities=[
    Instrumentation(settings=InstrumentationSettings(include_content=False)),
])
# or to instrument all agents:
Agent.instrument_all(InstrumentationSettings(include_content=False))
```

`include_model_request_parameters=False` exists for size rather than privacy: an MCP toolset carrying a large output schema can make the attribute big enough to strain span export and inflate memory use[^pydantic-logfire-docs] **Synthesis:** that makes it an export reliability setting that happens to have a confidentiality side effect, since the tool schemas it removes describe the agent's capability surface.

## Custom metadata and the first-run banner

The agent's `metadata` parameter is attached data, and when instrumentation is enabled the computed metadata is recorded on the agent span under the `metadata` attribute[^pydantic-logfire-docs] It is not one of the redaction switches' targets[^pydantic-logfire-docs]

The banner is the inverse signal — the notice that nothing is instrumented[^pydantic-logfire-docs] Until instrumentation is configured, the first agent run in a process prints a short message to `stderr`, shown only where someone is there to read it: when `stderr` is a terminal, or when a coding agent is running the process and reads back what it writes[^pydantic-logfire-docs] It never appears when instrumentation is configured, under `pytest`, when `CI` is set to any value, or for a run that an installed package (code in `site-packages`) starts by calling the agent itself — so a library or platform built on Pydantic AI does not show it to its own users, while the next run the host's own code starts still gets it, as does a run a UI adapter streams to a web app[^pydantic-logfire-docs]

To turn it off, set `PYDANTIC_AI_NO_BANNER` to any value, or set `pydantic_ai.BANNER_ENABLED = False` before the first agent run[^pydantic-logfire-docs] Coding agents are recognized by the environment variables they set for the purpose; the list is described as best-effort and always behind, so an unrecognized harness — including one built on Pydantic AI — sets `AI_AGENT` (or `AGENT`) to be treated the same way, naming itself in the value[^pydantic-logfire-docs]

## Limits

- One vendor reference page naming **no Pydantic AI version, publication date, author or licence**, so this page is `draft` under the `pydantic-ai` domain rule with a `stale_after`; which release introduced each format version is unstated[^pydantic-logfire-docs]
- The page numbers its own formats 2–6 but never describes format 1 or says how long a deprecated version stays selectable, and it does not give the complete attribute set for any version — only what each version changed[^pydantic-logfire-docs]
- The GenAI semantic conventions are described as still experimental and likely to change, so the version numbers here track a moving external spec as well as Pydantic AI's own emitter[^pydantic-logfire-docs]
- The `gen_ai.aggregated_usage.details.*` sub-attributes are named but not enumerated, the cost estimate's price source is deferred to a page not in this repository, and the metrics' aggregation temporality, the export cost of a large request-parameters attribute and whether a format version ever stops being accepted are unstated[^pydantic-logfire-docs]
- Nothing was installed, instrumented, exported, redacted or priced, and no span, metric or exception was inspected — every claim is **Reported**, none **Observed** or **Reproduced**.

## Relationships

- **Depends on** [Pydantic AI observability](pydantic-ai-observability.md) for enabling instrumentation, choosing a tracer provider and the export route this format travels over.
- **Carries** the `pydantic_ai.cache.*` attributes described in [Pydantic AI prompt-cache health](pydantic-ai-prompt-cache-health.md) on its model request spans.
- **Shapes** the `decide` span in [Logfire decision tracing](logfire-decision-tracing.md), which records usage under its own keys and emits no metrics for that reason.
- **Records** [model fallback](pydantic-ai-model-fallback.md) attempts on the same span tree, where the aggregated-usage rule keeps run totals addable.
- **Supplies** the `operation.cost` estimate that [Pydantic AI cost and spend limits](pydantic-ai-cost-and-spend-limits.md) enforces rather than reports.
- **Redacts** what [Pydantic AI workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md) keeps visible, since the workspace id survives `include_content=False`.

[^pydantic-logfire-docs]: Pydantic Docs, "Pydantic Logfire Debugging and Monitoring", <https://pydantic.dev/docs/ai/integrations/logfire/>, `domain: pydantic.dev`, `language: en`, 5,651 words as declared and 5,851 by local `wc -w`, 565 lines, no publication date, author, licence or Pydantic AI version; local capture `raw/integrations/logfire/index.md`, content digest sha256:5ea6a3e0. §"Pydantic Logfire" (raw lines 21–31) for the built-in-but-optional support and the no-overhead-when-unconfigured rule; §"Using Logfire" (lines 33–121) for the wizard, install routes, `logfire.configure()`/`instrument_pydantic_ai()`, agent `name=`, and the local-versus-production split; §"Monitoring HTTP Requests" (lines 152–179) for `instrument_httpx(capture_all=True)`, the `httpx`/`httpx2` provider SDKs with Bedrock on boto3, and the `opentelemetry-instrumentation-httpx>=0.65b0` requirement; §"Using OpenTelemetry" and §"Logfire with an alternative OTel backend" (lines 181–238) for the OTLP endpoint, `send_to_logfire=False` and the dual-send note; §"OTel without Logfire" (lines 239–281) for the raw SDK route; §"Prompt-cache health" (lines 288–332) for the attribute family, the collapse classification and the event rule, compiled in [prompt-cache health](pydantic-ai-prompt-cache-health.md); §"Emitted metrics" (lines 333–344) for the three histograms and their point attributes; §"Aggregated usage attribute names" (lines 345–361) for the aggregated names, the double-counting reason, the delegate exclusion and the disable switch; §"Configuring data format" (lines 362–435) for the conventions version, the v5 default, the deprecation warning, the version 2/3/4 feature lists, the v5 deferral rule and the version 6 role move including retry feedback; §"Setting OpenTelemetry SDK providers" (lines 436–456) for the global provider default and custom providers through `InstrumentationSettings`; §"Excluding binary content" (lines 457–475) for the binary flag, what keeps its media type, the file identifier rule and the user-type gap; §"Excluding prompts and completions" (lines 476–497) for `include_content=False`, the exception-type-only rule and the three things it does not cover; §"Excluding model request parameters" (lines 498–517) for the size motivation, the omitted attribute and the surviving `gen_ai.tool.definitions`; §"Decision model spans" (lines 518–558) for the no-metrics rule compiled on [Logfire decision tracing](logfire-decision-tracing.md); §"Adding Custom Metadata" (lines 559–565) for the `metadata` attribute and the banner's conditions, environment variables and coding-agent detection. Evidence class: **Reported** — vendor documentation; nothing was installed, instrumented, exported or inspected.
