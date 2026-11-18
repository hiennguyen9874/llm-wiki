---
type: Concept
title: Pydantic AI direct model requests
description: The `pydantic_ai.direct` module — five imperative request functions over the same `Model` classes an Agent uses, the request, tool-definition and response objects they take and return, when to drop below the Agent, and the per-call instrumentation switch.
tags: [pydantic-ai, models, direct-api, tools]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:35:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-direct-2026
    resource: ../raw/core-concepts/direct/index.md
    scope: ../raw/core-concepts/direct/
    kind: documentation
    revision: sha256:1b662ffdd5846ab4b373fbb3e78b9394bef70c1007219e2373d5b8b54166fff9
    title: "Direct Model Requests"
---

**Reported, Pydantic AI version unspecified:** `pydantic_ai.direct` is the layer between a `Model` and an `Agent` — a set of imperative functions that send a request and hand back a response, with input and output schema translation as the only abstraction they add[^pydantic-direct-2026] They are described as thin wrappers around the `Model` implementations, so the model classes and `<provider>:<model>` names a deployment already uses stay the same and only the orchestration around them is removed[^pydantic-direct-2026] That places the module at the bottom of the same stack [models and providers](pydantic-ai-models-and-providers.md) describes: the string still resolves to a model, a provider and a profile, but nothing runs the tool loop, retries a validation failure or parses structured output for you.

## The five functions

| Function | Shape |
| --- | --- |
| `model_request` | Non-streamed, async |
| `model_request_sync` | Non-streamed, synchronous |
| `model_request_stream` | Streamed, async |
| `model_request_stream_sync` | Streamed, synchronous |
| `model_request_batch` | Several requests through a model's batch API at lower cost |

The four request functions cover both the sync/async axis and the streamed/non-streamed one, and the fifth is the batch route: the page delegates its semantics to the batch-processing guide's "direct batch requests" section rather than restating them[^pydantic-direct-2026] Nothing in this capture states the functions' signatures, their keyword arguments beyond the samples below, or what a streamed return value looks like.

## A request without an agent

The minimal documented call passes a model name and a list of request messages, and reads `.text` and `.usage` off the returned `ModelResponse`[^pydantic-direct-2026]:

```python
from pydantic_ai import ModelRequest
from pydantic_ai.direct import model_request_sync

model_response = model_request_sync(
    'anthropic:claude-haiku-5-5',
    [ModelRequest.user_text_prompt('What is the capital of France?')]
)
print(model_response.usage)
#> RequestUsage(input_tokens=56, output_tokens=7)
```

Two parts of that sample are the durable content rather than the printout: a prompt is built with the `ModelRequest.user_text_prompt` classmethod instead of being written as a raw string, and the response carries usage as a `RequestUsage` with `input_tokens`/`output_tokens`[^pydantic-direct-2026] The model name is an unpinned alias and the printed token counts belong to the vendor's own run.

## Tool calling on the direct path

Tools are declarable without an agent, because the schema work is Pydantic's: a `BaseModel` supplies the JSON schema through `model_json_schema()`, and its class name and docstring become the tool's name and description[^pydantic-direct-2026] The definitions travel in a `ModelRequestParameters`:

```python
from pydantic_ai import ModelRequest, ToolDefinition
from pydantic_ai.models import ModelRequestParameters

model_response = await model_request(
    'openai:gpt-6-luna',
    [ModelRequest.user_text_prompt('What is 123 / 456?')],
    model_request_parameters=ModelRequestParameters(
        function_tools=[
            ToolDefinition(
                name=Divide.__name__.lower(),
                description=Divide.__doc__,
                parameters_json_schema=Divide.model_json_schema(),
            )
        ],
        allow_text_output=True,
    ),
)
```

Three details in that call are the ones to carry: `function_tools` takes raw `ToolDefinition` objects rather than callables, so the same definition surface as [tool definitions](pydantic-ai-tool-definitions.md) is used here without a `Tool` wrapper; `allow_text_output=True` is what lets the model answer in text instead of being forced into a tool call; and the model here is reached as `openai:gpt-6-luna`, a different alias from the Anthropic one in the first sample, with no change to the code[^pydantic-direct-2026] The response is a `ModelResponse` whose `parts` hold a `ToolCallPart` with `tool_name`, `args` and a `tool_call_id` in the `pyd_ai_…` form, alongside `usage`, `model_name` and `timestamp`[^pydantic-direct-2026]

**[Synthesis]** Nothing on the direct path executes the tool: the page's rationale for staying on `Agent` is precisely that the higher-level API adds "native tool execution", so on this path the caller inspects `parts`, runs the function itself, and builds the return message. The recorded sample also prints `args={'numerator': '123', 'denominator': '456'}` for a schema declaring `float` — numbers arriving as strings — which is consistent with no validation layer sitting between the provider's JSON and the caller here, and is a reason to validate arguments before invoking anything (**Synthesis**, from the printed transcript).

## Direct versus Agent

The page gives three conditions for the direct API, all of them about owning the surrounding logic: more direct control over model interactions, custom behaviour around the request, and building your own abstractions on top of model interactions[^pydantic-direct-2026] It answers the obvious question in the other direction too — for most application use cases the `Agent` remains the recommendation, because it adds native tool execution, retrying, and structured-output parsing[^pydantic-direct-2026] Anything the wiki records about the agent loop, retry budgets or output modes therefore does not apply to a call made here; the direct path is where you re-implement whichever of them you need.

## Instrumentation

Tracing reaches these calls, both globally and per request. The global route is the same pair of lines used for agents — `logfire.configure()` then `logfire.instrument_pydantic_ai()` — and the per-call route passes `instrument=True` to the request function[^pydantic-direct-2026] The page points at the Logfire integration guide for plain OpenTelemetry without Logfire; the spans produced are the ones [observability](pydantic-ai-observability.md) describes, though this capture does not say whether a direct request emits a run span, a `chat` span, or the model-request span alone.

## Limits

- The capture is vendor documentation naming **no Pydantic AI version**, no date, author or licence, so the page is `draft` under the `pydantic-ai` domain rule and every name here is version-unknown[^pydantic-direct-2026]
- Its six reference links — the `Model` base class, `Agent`, and the `pydantic_ai.direct` page for each function — were read as links, not followed, so no signature, default, return type or streamed-response shape is evidence here[^pydantic-direct-2026]
- The batch route is named only by pointer: this capture states that the page defers its semantics to the batch-processing guide's "direct batch requests" section without restating them, and that separate capture is now compiled as [direct batch requests](pydantic-ai-direct-batch-requests.md), with the agent-level half in [batch processing](pydantic-ai-batch-processing.md).
- Nothing was installed, no model constructed, no request sent, nothing streamed, no tool executed, no batch submitted and no span exported, so every claim here is **Reported** and none is **Observed** or **Reproduced**. The printed responses are vendor output, quoted rather than reproduced.
- Errors, retries, timeouts, concurrency limits and cancellation are not mentioned in the capture at all; [model API errors](pydantic-ai-model-api-errors.md) describes the failure taxonomy of the layer beneath, but which of those errors a direct call surfaces unchanged is unstated.

## Relationships

- **Uses** the model classes and `<provider>:<model>` resolution described in [models and providers](pydantic-ai-models-and-providers.md), as thin wrappers rather than a second abstraction.
- **Passes** the same `ToolDefinition` structure as [tool definitions](pydantic-ai-tool-definitions.md), with no `Tool` object or automatic execution around it.
- **Is instrumented into** the spans [observability](pydantic-ai-observability.md) documents, through `instrument_pydantic_ai()` or a per-call `instrument=True`.
- **Defers** its batch function to [direct batch requests](pydantic-ai-direct-batch-requests.md), the `model_request_batch` and `Model.batch_*` half of the same guide.
- **Contrasts with** [image generation](pydantic-ai-image-generation.md)'s `ImageGenerator`, the other direct, agent-less API in Pydantic AI, which returns typed media instead of a `ModelResponse`.

[^pydantic-direct-2026]: Pydantic Docs, "Direct Model Requests" (<https://pydantic.dev/docs/ai/core-concepts/direct/>, `domain: pydantic.dev`, `language: en`, 539 words as declared and 595 by local `wc -w` including frontmatter and markup; no publication date, author, licence or Pydantic AI version); local capture `raw/core-concepts/direct/index.md`, content digest sha256:1b662ffd. Lines 9–19 for the module's purpose as thin wrappers over the `Model` implementations and the five-function list; §"Basic Example" (lines 23–45) for `model_request_sync`, `ModelRequest.user_text_prompt`, the `anthropic:claude-haiku-5-5` alias, `.text` and the printed `RequestUsage(input_tokens=56, output_tokens=7)`; §"Advanced Example with Tool Calling" (lines 47–102) for `model_request` with `ModelRequestParameters(function_tools=[ToolDefinition(...)], allow_text_output=True)`, the `Divide` model's `model_json_schema()`/`__doc__`/`__name__` inputs, `openai:gpt-6-luna`, and the printed `ModelResponse` with a `ToolCallPart`, `usage`, `model_name` and `timestamp`; §"When to Use the direct API vs Agent" (lines 104–112) for the three conditions and the Agent's native tool execution, retrying and structured-output parsing; §"OpenTelemetry or Logfire Instrumentation" (lines 114–162) for `logfire.configure()`, `logfire.instrument_pydantic_ai()` and the per-call `instrument=True`. Evidence class: **Reported** — vendor documentation and its printed sample output; nothing was installed, requested, streamed, executed or instrumented.
