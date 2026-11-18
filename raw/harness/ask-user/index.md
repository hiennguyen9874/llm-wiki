---
title: "Ask User"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/harness/ask-user/"
domain: "pydantic.dev"
language: "en"
description: "Let a Pydantic AI agent ask the user clarifying multiple-choice questions mid-run and wait for answers, from a terminal, web UI, or test answerer you supply."
word_count: 4095
---

Let the model ask the user multiple-choice questions mid-run and wait for the answers.

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/ask_user/)

> While Pydantic AI Harness is on 0.x releases, the API may change between minor releases; when it does, deprecation warnings and release-note migration guidance tell you (or your agent) exactly how to upgrade. See the [version policy](https://pydantic.dev/docs/ai/harness/#version-policy).

```
flowchart TB
    accTitle: Ask User: the model asks multiple-choice questions mid-run
    accDescr: The model sends questions to ask_user_question on AskUser and gets the picked labels. AskUser rejects calls outside the limits or with control characters as a retry and passes an AskUserRequest to the answerer, a terminal menu or web form, which asks the user the questions and returns the picks as an AskUserResponse. With answerer=None, the run pauses with DeferredToolRequests.
    model(["model"])
    ask["AskUser()<br/>ask_user_question"]:::capability
    rejected["outside the limits or<br/>control characters"]:::blocked
    answerer["answerer<br/>terminal menu<br/>or web form"]
    paused["run pauses with<br/>DeferredToolRequests"]
    user(["user"])
    model <-->|"questions, picked labels"| ask
    ask -.-x|"rejects as a retry"| rejected
    ask <-->|"AskUserRequest,<br/>AskUserResponse"| answerer
    ask -.->|"answerer=None"| paused
    answerer <-->|"questions, picks"| user
    classDef capability stroke:#E520E9,stroke-width:2px
    classDef blocked stroke:#E5533D,stroke-width:2px,stroke-dasharray:4 3
```

## Usage

`AskUser` exposes one tool, `ask_user_question`. The model passes one to ten questions, each with a short `header`, the question text, two to six options (a `label` and an optional `description`), and `multi_select` when several answers are allowed. The capability validates the call, hands it to your `answerer`, and returns the picked labels keyed by header. If the user declines, the model is told so and the run continues.

The capability never prints, reads stdin, or imports a terminal library: the `answerer` is whatever puts the questions in front of a person, and you supply it. There is no default, because an answerer that reads stdin would not work from a server.

```python
from pydantic_ai import Agent
from pydantic_ai_harness import AskUser
from pydantic_ai_harness.ask_user import AskUserAnswer, AskUserRequest, AskUserResponse

async def pick_first(request: AskUserRequest) -> AskUserResponse:
    answers = [AskUserAnswer(header=q.header, selected=(q.options[0].label,)) for q in request.questions]
    return AskUserResponse(answers=tuple(answers))

agent = Agent('anthropic:claude-fable-5-2', capabilities=[AskUser(answerer=pick_first)])
```

`pick_first` stands in for a real UI. [CLAI](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_clai2/) ships a terminal menu built on the same protocol; a web form would be another.

## Writing an answerer

An `Answerer` is one async callable: it takes an `AskUserRequest` and returns an `AskUserResponse`. A plain `async def` qualifies; a class with `async def __call__` does too.

- `AskUserRequest.questions` holds the validated `Question` objects; `AskUserRequest.id` distinguishes concurrent or repeated calls so a UI can match its reply to the request.
- A completed `AskUserResponse` carries one `AskUserAnswer` per question, keyed by `header`, with the picked option labels in `selected`: exactly one unless the question is `multi_select`, at least one either way, and no label twice.
- An answerer may instead return `AskUserAnswer(header=q.header, custom_answer='My own answer')`. Leave `selected` empty. Custom text must be nonblank and follow the question fields’ [character rules](#what-the-model-sees), with newlines allowed, so run `check_response` on text a user typed. Its length is not limited, so cap free text that arrives from a client before returning it. The model receives it as a one-item list under the question’s header. Whether to offer text entry is up to the answerer; the model cannot request it.
- When the user declines, return `AskUserResponse(cancelled=True)` with no answers. The tool result tells the model the user declined; nothing is raised into the run.
- A response that does not fit the request (an unknown header, a label the question did not offer, several labels on a single-select question, a missing answer) is a bug in the answerer and raises `ValueError`, which fails the run. `check_response` is exported so an answerer can validate before returning.
- Two `ask_user_question` calls in one model response reach the answerer one at a time, after the response’s other tool calls have finished: an answer shapes the model’s next response, not calls it already made.
- The model writes the questions, and a prompt injection can make it ask for a password or a token. Present the questions as coming from the model, not as a system or sign-in prompt.

### Reading the asking run

An answerer with two required positional parameters receives `(ctx, request)`, satisfying [`ContextAnswerer`](https://pydantic.dev/docs/ai/harness/ask-user/#pydantic_ai_harness.ask_user.ContextAnswerer). Request-only answerers keep receiving just the request. Both plain async functions and callable objects are supported, including two-argument lambdas.

If a callable accepts both one and two positional arguments, annotate its first parameter as \[`RunContext[DepsT]`\]\[pydantic\_ai.tools.RunContext\] to select the context form; otherwise it receives only the request. Only the first annotation is inspected; an unresolved annotation naming `RunContext` also selects the context form. Use \[`AnyAnswerer[DepsT]`\]\[pydantic\_ai\_harness.ask\_user.AnyAnswerer\] to annotate a stored callback that may use either signature.

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai_harness import AskUser
from pydantic_ai_harness.ask_user import AskUserAnswer, AskUserRequest, AskUserResponse

async def answer_for_session(ctx: RunContext[str], request: AskUserRequest) -> AskUserResponse:
    for question in request.questions:
        print(f'{ctx.deps}: {question.question}')
    answers = [AskUserAnswer(header=q.header, selected=(q.options[0].label,)) for q in request.questions]
    return AskUserResponse(answers=tuple(answers))

agent = Agent('anthropic:claude-fable-5-2', deps_type=str, capabilities=[AskUser(answerer=answer_for_session)])
```

In an in-process run, `ctx.deps`, `ctx.model`, and `ctx.messages` belong to the run that called the tool. For a delegated agent, that is the child’s run, not the parent’s. The messages include the model response that asked the question, including thinking parts when the model provides them, and `ctx.tool_call_id` is the question’s call. Treat the history as read-only.

The context reaches only the answerer; it is not part of the request, its events or deferred calls. With `answerer=None`, no answerer is called: deferred hosts supply context from their own state. Durable execution can restrict access to context fields; see [Temporal’s run-context rules](https://pydantic.dev/docs/ai/capabilities/durable_execution/temporal/#agent-run-context-and-dependencies).

## Adding notes to an answer

Set [`AskUserAnswer.note`](https://pydantic.dev/docs/ai/harness/ask-user/#pydantic_ai_harness.ask_user.AskUserAnswer.note) to a tuple of [`UserContent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UserContent) items to accompany selected labels or a custom answer. Text and images keep their order; notes do not replace the required answer.

```python
from pydantic_ai.messages import ImageUrl
from pydantic_ai_harness.ask_user import AskUserAnswer

answer = AskUserAnswer(
    header='Database',
    selected=('Postgres',),
    note=('Keep version 16. Match this layout:', ImageUrl('https://example.com/schema.png')),
)
```

Text, including `TextContent`, follows the custom-answer character rules. A nonempty note must contain nonblank text or an attachment, not only whitespace or cache markers. Run `check_response(request, response)` before submitting client input. The harness sets no note size limit; the answerer should bound text and attachments from clients.

File URLs must use HTTP(S) and `force_download=False`. Notes reject other URL schemes, forced download modes (including `True` and `'allow-local'`), Google Files API URLs and `UploadedFile` provider references, even when a server-side answerer constructed them. To attach a file instead, have the application authorize access and supply its bytes as `BinaryContent`.

Only the rendered text of `TextContent` and `StructuredContent` is forwarded; user-supplied text metadata is dropped so notes cannot claim framework provenance. The answered event still carries the original response before validation, so observers must treat its note metadata as user input.

With notes, `ask_user_result` returns a [`ToolReturn`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ToolReturn): `return_value` is the unchanged answer dictionary, and `content` sends the notes as [`UserPromptPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UserPromptPart) content rather than tool data. Each note is framed by `<answer_note header="...">` and `</answer_note>` text items. Headers and framing tags inside text are escaped; images remain multimodal items between those boundaries. The boundary items are `TextContent` with `metadata` containing `origin='user.pydantic-ai-harness.ask_user.answer_note.v1'`, `request_id` and `header`, so applications can identify the record without matching visible text. The user-content origin keeps notes classified as user turns during compaction. Without notes, the result is the answer dictionary or decline text.

Annotate results with [`AskUserResult`](https://pydantic.dev/docs/ai/harness/ask-user/#pydantic_ai_harness.ask_user.AskUserResult). To inspect wrapped answers, narrow with `isinstance(result, ToolReturn)` and read `result.return_value`. Deferred hosts can pass the result directly to `DeferredToolResults.calls`.

## Bounding the wait

The run waits for the answer. Set `timeout`, in seconds, to bound that wait. When it runs out, or a resume token is resolved with a failure instead of an answer, `AskUserAnsweredEvent` fires with `timed_out=True` and a cancelled response, and the model is told the user did not answer in time (the `TIMED_OUT` result) and continues.

In process, the timeout cancels an answerer still running, so the answerer must be cancellable. A thread cannot be cancelled: run blocking work with `anyio.to_thread.run_sync(..., abandon_on_cancel=True)`, or the run waits for the thread and then uses its late answer. An abandoned thread keeps running, so a terminal answerer should read input with an async prompt library rather than `input()` in a thread, which would take the next line the user types.

```python
AskUser(answerer=pick_first, timeout=300)
```

## Answering later, and durable runs

Each question is a [deferred tool call](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/) marked as a question: the tool raises `CallDeferred(kind='question')`, so `DeferredToolRequests.kind()` reports `'question'` for it. `AskUser` then answers its own questions in its `handle_deferred_tool_calls` hook, one at a time, by calling the answerer through `wait_for_external_event`, the same wait a [`HandleDeferredToolCalls` handler that takes a resume token](https://pydantic.dev/docs/ai/capabilities/handle-deferred-tool-calls/#a-handler-that-takes-a-token) uses. That makes the wait durable on an engine that supports it:

- In a plain run, the answerer is called in process.
- On [AWS Lambda durable functions](https://pydantic.dev/docs/ai/harness/aws-lambda/#approvals), the answerer runs in a step that records its response, so a replay doesn’t ask again. Since it runs in a step, it must return quickly: a person who may take a while should answer through a resume token, below.
- On Temporal, DBOS, Prefect and other durable engines without support for waiting, the engine refuses the wait with a `UserError`. A wait in process would not be recorded: a replay would ask the user again, could get a different answer than the one the run already acted on and diverge from the engine’s history, and a restart would lose the wait.

An answerer with three required positional parameters, satisfying `TokenAnswerer`, also receives a resume token. It can answer right away as the other forms do, or hand the token on, for example in a Slack message, and return `None`. The answer then arrives when your code resolves the token with the JSON form of an `AskUserResponse`: with `resolve_external_event` from `pydantic_ai.external_events` in process, or through the engine’s API, such as AWS Lambda’s `SendDurableExecutionCallbackSuccess`.

```python
from pydantic import TypeAdapter

from pydantic_ai import Agent, RunContext
from pydantic_ai.external_events import resolve_external_event
from pydantic_ai_harness import AskUser
from pydantic_ai_harness.ask_user import AskUserRequest, AskUserResponse

pending: dict[str, AskUserRequest] = {}

async def hand_on(ctx: RunContext, request: AskUserRequest, token: str) -> AskUserResponse | None:
    pending[token] = request  # Show the questions where the user will see them.
    return None

def answer(token: str, response: AskUserResponse) -> None:
    # Runs in the endpoint the user's answer is posted to.
    pending.pop(token)
    resolve_external_event(token, TypeAdapter(AskUserResponse).dump_python(response, mode='json'))

agent = Agent('anthropic:claude-fable-5-2', capabilities=[AskUser(answerer=hand_on)])
```

Because the question is a deferred call, it waits until the other tool calls from the same model response have finished.

`AskUser` answers its questions before a `HandleDeferredToolCalls` handler is asked about what’s left, wherever you list them, and its answer passes the tool’s `after_tool_execute` hooks, such as result guards, as it did when the tool waited for it. To handle every pending call in one place instead, pass `answerer=None` and answer the question in a `HandleDeferredToolCalls` handler with `ask_user_result`, as the next section shows for a later run.

## Pausing the run until the user answers

A web server or a durable worker often cannot hold a run open while a person decides. Pass `answerer=None` and every `ask_user_question` call is [deferred](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/) instead: the run ends with `DeferredToolRequests` output, so your `output_type` must include it, and you answer in a later run, from the same process or another one.

- `AskUserRequest.from_tool_call(call)` rebuilds the validated request from a pending call. Its `id` is the call’s `tool_call_id`, the same request `AskUserRequestedEvent` carried before the run paused.
- `ask_user_result(request, response)` checks the response like an answerer’s (raising `ValueError` if it does not fit) and renders the tool result the model would have got inline. Pass it in `DeferredToolResults.calls` under the call’s ID.
- No `AskUserAnsweredEvent` fires for a deferred call: the answer comes from you, in the next run.
```python
from pydantic_ai import Agent, AgentRunResult, DeferredToolRequests, DeferredToolResults, ModelMessage
from pydantic_ai_harness import AskUser
from pydantic_ai_harness.ask_user import TOOL_NAME, AskUserRequest, AskUserResponse, ask_user_result

agent = Agent(
    'anthropic:claude-fable-5-2',
    output_type=[str, DeferredToolRequests],
    capabilities=[AskUser(answerer=None)],
)

def pending_questions(requests: DeferredToolRequests) -> dict[str, AskUserRequest]:
    """What the paused run is waiting on, keyed by tool call ID: show these to the user."""
    return {
        call.tool_call_id: AskUserRequest.from_tool_call(call)
        for call in requests.calls
        if call.tool_name == TOOL_NAME
    }

async def resume(
    messages: list[ModelMessage],
    questions: dict[str, AskUserRequest],
    responses: dict[str, AskUserResponse],
) -> AgentRunResult[str | DeferredToolRequests]:
    """Answer the paused run's questions and carry on."""
    calls = {call_id: ask_user_result(request, responses[call_id]) for call_id, request in questions.items()}
    return await agent.run(message_history=messages, deferred_tool_results=DeferredToolResults(calls=calls))
```

Keep the paused run’s `all_messages()` and its pending questions wherever you keep sessions, then call `resume` when the answers arrive. `timeout` needs an answerer to bound, so combining it with `answerer=None` raises `UserError`.

## Watching without answering

Two `CapabilityEvent`s let anything else in the run observe the exchange:

| Event | When | Fields |
| --- | --- | --- |
| `AskUserRequestedEvent` | before the answerer is called, or before a deferred call pauses the run | `request` |
| `AskUserAnsweredEvent` | after it returns, times out, or raises, or its resume token is resolved or failed, before the response is checked or the model sees the result | `request_id`, `response`, `timed_out`, `failed` |

Both dispatch immediately, so a listener that shows a “waiting for you” state sees the wait start and end in step with the run. When the answerer raises, or a resume token is resolved with something that isn’t an `AskUserResponse`, the answered event carries `failed=True` and a cancelled response, then a `ModelRetry` from the answerer sends the model a retry prompt, and any other error fails the run. A run cancelled while the answerer waits emits no answered event, so also clear waiting state when the run ends. Subscribe with `@on_event` on a capability or through the run’s event stream:

```python
from pydantic_ai import RunContext
from pydantic_ai.capabilities import AbstractCapability, on_event

from pydantic_ai_harness.ask_user import AskUserAnsweredEvent, AskUserRequestedEvent

class WaitIndicator(AbstractCapability[None]):
    @on_event(AskUserRequestedEvent)
    async def waiting(self, ctx: RunContext[None], event: AskUserRequestedEvent) -> None:
        print(f'waiting on {len(event.request.questions)} question(s)')

    @on_event(AskUserAnsweredEvent)
    async def done(self, ctx: RunContext[None], event: AskUserAnsweredEvent) -> None:
        if event.failed:
            print('failed')
        elif event.timed_out:
            print('timed out')
        else:
            print('declined' if event.response.cancelled else 'answered')
```

## What the model sees

The tool schema mirrors [Code Puppy](https://github.com/mpfaffenberger/code_puppy)’s `ask_user_question`, so prompts written for it carry over.

| Field | Limit |
| --- | --- |
| `questions` | 1 to 10 per call; headers unique, ignoring case and compatibility forms such as full-width letters |
| `header` | 1 to 25 characters, one line |
| `question` | 1 to 500 characters, may span lines |
| `options` | 2 to 6 per question; labels unique, ignoring case and compatibility forms such as full-width letters |
| `label` | 1 to 50 characters, one line |
| `description` | optional, at most 200 characters, may span lines |

These strings are drawn on terminals, where an escape sequence in a prompt-injected call is an attack, so control characters and format characters such as zero-width spaces, joiners and bidirectional overrides are rejected. Spaces of any width are allowed, and uniqueness treats most of them as an ordinary space. A call outside these limits, or with a field the schema does not have, goes back to the model as a validation retry and never reaches the answerer. Once validated the questions are frozen: what the answerer sees is what the model asked.

The result is a JSON object mapping each header to the list of picked labels (or one custom answer), or the sentence `The user declined to answer. Continue without the answer, or ask differently if it is essential.` When `timeout` runs out, it is the `TIMED_OUT` sentence instead.

The capability adds one instruction: ask when the task is ambiguous and the answer is not in the workspace, offer concrete options, batch related questions, and make a stated choice if the user declines.

## One per agent

`AskUser` declares the default `id` `'ask_user'`. The `id` keys the capability’s instructions, so they can be addressed, and lets `defer_loading=True` work without one. Two `AskUser`s on one agent that share it are one answerer stated twice: they become one when they agree, and the agent raises a `UserError` when it’s built if they differ. To keep two, give each its own `id` and wrap them in [PrefixTools](https://pydantic.dev/docs/ai/capabilities/prefix-tools/), since both register `ask_user_question`. To serve several UIs, pass one answerer that dispatches to them.

## Tracing

`AskUser` emits no spans. Core’s tool-call span records the questions as the tool’s arguments, and the two events above carry what was asked and answered. The answers, custom text, notes and attachments included, appear in the following model request’s tool result and user content. The `include_content` setting applies to notes as well. Set [`include_content=False`](https://pydantic.dev/docs/ai/integrations/logfire/#excluding-prompts-and-completions) to leave them out.

## Specs

`Agent.from_spec` cannot construct `AskUser`: the answerer is a live object a spec has no way to name.

## API reference

`check_response`, `ask_user_result`, `AskUserResult`, `TokenAnswerer`, `TOOL_NAME`, `DECLINED`, `TIMED_OUT`, and `MAX_QUESTIONS` are also exported from `pydantic_ai_harness.ask_user`, along with `AskUserToolset`, the toolset `AskUser` registers, and `ASK_USER_EVENTS`, the namespace of both events.

### AskUser

**Bases:** `AbstractCapability[AgentDepsT]`

Let the model ask the user multiple-choice questions mid-run.

The capability owns the question schema and validation; the `answerer` owns the person. Whatever it is, a terminal menu, a web form, or a scripted function in a test, the run waits for its answer and the model gets the picked labels back. Pass `answerer=None` to end the run with `DeferredToolRequests` instead, so the host answers in a later run.

Each question is a deferred tool call marked as a question, and the answerer is called from `handle_deferred_tool_calls` through `wait_for_external_event`, as `HandleDeferredToolCalls` calls a handler that takes a resume token. So the wait is in process in a plain run, and recorded by the engine in a durable run on an engine that supports it, such as AWS Lambda durable functions; other durable engines refuse it.

```python
from pydantic_ai import Agent
from pydantic_ai_harness import AskUser
from pydantic_ai_harness.ask_user import AskUserAnswer, AskUserRequest, AskUserResponse

async def pick_first(request: AskUserRequest) -> AskUserResponse:
    answers = [AskUserAnswer(header=q.header, selected=(q.options[0].label,)) for q in request.questions]
    return AskUserResponse(answers=tuple(answers))

agent = Agent('anthropic:claude-fable-5-2', capabilities=[AskUser(answerer=pick_first)])
```

#### Attributes

##### answerer

Presents each `AskUserRequest` to the user and returns their `AskUserResponse`.

An answerer with two required positional parameters receives the asking run’s context before the request. If it also accepts just one, annotate the first as `RunContext[DepsT]` to select the context form. Request-only answerers receive just the request. An answerer with three required positional parameters also receives a resume token, and may return `None` after handing the token on: the answer then arrives when the token is resolved with an `AskUserResponse`.

In a durable run, the answerer runs inside a durable unit that records its response, so it must return quickly: a person who may take a while should answer through the token.

`None` defers every call: the run ends with `DeferredToolRequests` output, and the host answers in a later run with `ask_user_result` in `DeferredToolResults.calls`.

**Type:** `AnyAnswerer`\[`AgentDepsT`\] | [`None`](https://docs.python.org/3/builtins/constants.html#None)

##### timeout

Seconds to wait for an answer before telling the model the user did not answer.

In process, an async answerer still running then is cancelled. Must be positive; `None` waits indefinitely. Needs an answerer: a deferred call has nothing to wait on.

**Type:** [`float`](https://docs.python.org/3/builtins/functions.html#float) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### id

Stable capability ID, so its instructions are addressable and `defer_loading=True` needs none.

An agent has one `ask_user_question` tool, so two `AskUser` sharing this `id` are one answerer stated twice when they agree, and an error when they differ. To keep two, give each its own `id` and wrap them in `PrefixTools`, since their tool names are the same.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `'ask_user'`

#### Methods

##### combine

`@classmethod`

```python
def combine(
    cls,
    capabilities: Sequence[AbstractCapability[AgentDepsT]],
) -> AbstractCapability[AgentDepsT]
```

Two under one `id` are one answerer stated twice; two that disagree raise rather than merge.

###### Returns

`AbstractCapability`\[`AgentDepsT`\]

##### get\_instructions

```python
def get_instructions() -> AgentInstructions[AgentDepsT] | None
```

Static, cache-stable guidance on when to ask.

###### Returns

`AgentInstructions`\[`AgentDepsT`\] | [`None`](https://docs.python.org/3/builtins/constants.html#None)

##### get\_ordering

```python
def get_ordering() -> CapabilityOrdering
```

Answer its own questions before a `HandleDeferredToolCalls` handler sees the pending calls, wherever it is listed.

A generic handler that fills every call in `requests.calls` would otherwise answer the question itself, and the answerer would never be asked. A handler that takes a resume token is innermost, so it comes later still.

###### Returns

`CapabilityOrdering`

##### get\_toolset

```python
def get_toolset() -> AgentToolset[AgentDepsT] | None
```

The `ask_user_question` tool, which defers each call as a question this capability answers.

###### Returns

[`AgentToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AgentToolset) \[`AgentDepsT`\] | [`None`](https://docs.python.org/3/builtins/constants.html#None)

##### handle\_deferred\_tool\_calls

`@async`

```python
def handle_deferred_tool_calls(
    ctx: RunContext[AgentDepsT],
    *,
    requests: DeferredToolRequests,
) -> DeferredToolResults | None
```

Answer this capability’s own questions with the answerer, one at a time; leave other calls to later handlers.

###### Returns

[`DeferredToolResults`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolResults) | [`None`](https://docs.python.org/3/builtins/constants.html#None)

### Answerer

**Bases:** [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Whatever puts the questions in front of a person: a terminal menu, a web form, a scripted test.

A plain `async def` with this signature satisfies it. Return a cancelled response when the user declines; raise only for failures that should fail the run.

#### Methods

##### \_\_call\_\_

`@async`

```python
def __call__(request: AskUserRequest, /) -> AskUserResponse
```

Put `request` to the user and return what they picked.

###### Returns

`AskUserResponse`

### ContextAnswerer

**Bases:** `Protocol[AgentDepsT]`

An answerer that also receives the context of the run that asked the question.

Two required positional parameters select this form. If a callable also accepts just one, annotate the first parameter as `RunContext[DepsT]` to disambiguate. The request and response follow the same contract as `Answerer`; the context is passed separately, not serialized into `AskUserRequest` or its events. Durable execution can restrict context fields; see [Temporal’s run-context rules](https://pydantic.dev/docs/ai/capabilities/durable_execution/temporal/#agent-run-context-and-dependencies).

#### Methods

##### \_\_call\_\_

`@async`

```python
def __call__(ctx: RunContext[AgentDepsT], request: AskUserRequest, /) -> AskUserResponse
```

Put `request` to the user with access to the asking run’s context.

###### Returns

`AskUserResponse`

### TokenAnswerer

**Bases:** `Protocol[AgentDepsT]`

An answerer that may hand the question on and let the answer arrive later, through a resume token.

Three required positional parameters select this form. Return the response to answer right away, as the other forms do, or `None` after delivering `token` to whoever will answer, such as in a Slack message. The run then waits until the token is resolved with the JSON form of an `AskUserResponse`: with `pydantic_ai.external_events.resolve_external_event` in process, or through the durable engine’s API, such as AWS Lambda’s `SendDurableExecutionCallbackSuccess`.

#### Methods

##### \_\_call\_\_

`@async`

```python
def __call__(
    ctx: RunContext[AgentDepsT],
    request: AskUserRequest,
    token: str,
    /,
) -> AskUserResponse | None
```

Answer `request`, or deliver `token` and return `None`.

###### Returns

`AskUserResponse` | [`None`](https://docs.python.org/3/builtins/constants.html#None)

### AnyAnswerer

Any answerer signature, for hosts storing a callback to pass to `AskUser`.

`Answerer` remains the request-only protocol; `ContextAnswerer` also receives the asking run’s context, and `TokenAnswerer` also a resume token, so it can let the answer arrive later.

**Type:** [`TypeAlias`](https://docs.python.org/3/library/typing.html#typing.TypeAlias) **Default:** `Answerer | ContextAnswerer[AgentDepsT] | TokenAnswerer[AgentDepsT]`

### AskUserRequest

One `ask_user_question` call, handed to the `Answerer` and carried by `AskUserRequestedEvent`.

#### Attributes

##### id

Distinguishes concurrent or repeated calls; a UI matches its reply to it.

A deferred request uses the tool call ID, so `from_tool_call` rebuilds the same request.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) **Default:** `field(default_factory=(lambda: uuid4().hex))`

#### Methods

##### from\_tool\_call

`@classmethod`

```python
def from_tool_call(cls, call: ToolCallPart) -> AskUserRequest
```

Rebuild the request behind a deferred `ask_user_question` call, to put it to the user.

Raises `ValueError` when `call` is for another tool.

###### Returns

`AskUserRequest`

### AskUserResponse

What the `Answerer` returns: one answer per question, or `cancelled` when the user declined.

### AskUserAnswer

Picked labels, or a custom answer instead, with optional user notes for one question.

#### Attributes

##### note

User text and attachments, in order, accompanying either selected labels or a custom answer.

Text follows the custom-answer character rules. A nonempty note must contain nonblank text or an attachment, not only whitespace or cache markers. Notes do not replace the answer. File URLs must use HTTP(S) with `force_download=False`; provider-uploaded file references are not accepted. Text metadata is not forwarded to message history.

**Type:** [`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple) \[[`UserContent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UserContent), …\] **Default:** `()`

### AskUserResult

The answer dictionary or decline text, wrapped in `ToolReturn` when user notes accompany the answers.

**Type:** [`TypeAlias`](https://docs.python.org/3/library/typing.html#typing.TypeAlias) **Default:** `ToolReturn[dict[str, list[str]]] | dict[str, list[str]] | str`

### Question

**Bases:** `BaseModel`

One multiple-choice question.

### QuestionOption

**Bases:** `BaseModel`

One choice the user can pick.

### AskUserRequestedEvent

**Bases:** [`CapabilityEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.CapabilityEvent)

The model asked the user something; the call is deferred, for `AskUser`’s answerer or the host to answer.

### AskUserAnsweredEvent

**Bases:** [`CapabilityEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.CapabilityEvent)

The answer arrived, from the answerer or through its resume token, or the wait timed out or failed.

If an answer arrived, `response.cancelled` says whether the user declined. Emitted before the response is checked against the request, so a listener waiting since the request event is released even when the answerer misbehaved and the run is about to fail. Not emitted with `answerer=None`, whose answer arrives in a later run from the host, or when the run itself is cancelled while it waits: clear waiting state when the run ends.

#### Attributes

##### timed\_out

No answer arrived within `AskUser.timeout`, or the resume token was resolved with a failure; `response` is then a cancelled one.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `False`

##### failed

The answerer raised, or the token was resolved with something that isn’t an `AskUserResponse`; `response` is then a cancelled one, and the error fails the run, or a `ModelRetry` asks the model to retry.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `False`
