---
type: Concept
title: Pydantic AI Harness ask user
description: The Harness AskUser capability — one ask_user_question tool with a bounded schema, an answerer you supply because there is no default, three failure paths (decline, timeout, pause as a deferred call), a resume-token form for durable runs, and the terminal-injection rules its fields enforce.
tags: [pydantic-ai, agents, harness, human-in-the-loop]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:21:19Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-ask-user-docs
    resource: ../raw/harness/ask-user/index.md
    scope: ../raw/harness/ask-user/
    kind: documentation
    revision: sha256:4ac2bacc21606393716c3c61c456e28114383de4ccb1f7bbc328090e94efb1da
    title: "Ask User"
---

`AskUser` is the [Harness](pydantic-ai-harness.md) capability that lets a model ask the **person** multiple-choice questions mid-run and wait for the answers, through one tool, `ask_user_question`[^pydantic-ask-user-docs] Its defining decision is what it does *not* ship: there is **no default answerer**, because an answerer that reads stdin would not work from a server, and the capability itself never prints, reads stdin or imports a terminal library. It owns the question schema and validation; you own the person. Reaching a person mid-run is the synchronous sibling of [deferred tool approval](pydantic-ai-deferred-approvals.md), which pauses the run instead of waiting. The page names no Pydantic AI or Harness version, so every behaviour below is version-unknown.

## The question schema is the safety surface

The tool's arguments are constrained before anything reaches a person, and every limit is aimable at a terminal[^pydantic-ask-user-docs]:

| Field | Limit |
| --- | --- |
| `questions` | 1 to 10 per call; `header`s unique, ignoring case and compatibility forms such as full-width letters |
| `header` | 1–25 characters, one line |
| `question` | 1–500 characters, may span lines |
| `options` | 2–6 per question; labels unique, same compatibility rule |
| `label` | 1–50 characters, one line |
| `description` | optional, at most 200 characters, may span lines |

Because these strings are drawn on terminals, **control and format characters are rejected** — zero-width spaces, joiners, bidirectional overrides — since an escape sequence in a prompt-injected call is an attack; spaces of any width are allowed and uniqueness treats most of them as ordinary[^pydantic-ask-user-docs] A call outside the limits, or carrying a field the schema lacks, returns to the model as a **validation retry** and never reaches the answerer. Once validated the questions are **frozen**, so what the answerer shows is what the model asked.

The schema mirrors Code Puppy's `ask_user_question`, so prompts written for it carry over. The model can only ask multiple choice: free-text entry exists for the **answerer** to offer, never for the model to request[^pydantic-ask-user-docs]

One instruction is added: ask when the task is ambiguous and the answer is not in the workspace, offer concrete options, batch related questions, and make a stated choice if the user declines. And one warning belongs in any integration: a prompt injection can make the model ask for a password or a token, so the UI must present questions **as coming from the model**, not as a system or sign-in prompt[^pydantic-ask-user-docs]

## The three answerer signatures

An `Answerer` is one async callable taking an `AskUserRequest` and returning an `AskUserResponse`[^pydantic-ask-user-docs] The arity you write selects the form:

| Signature | Receives | For |
| --- | --- | --- |
| `async def(request)` | The validated questions | A menu, a form, a scripted test stub |
| `async def(ctx, request)` | Plus the asking run's `RunContext` | Session-aware UIs that need `deps`, the model, or the messages |
| `async def(ctx, request, token)` | Plus a resume token | Durable hosts, where a person may take a long time |

Ambiguity is resolved by annotating the first parameter as `RunContext[DepsT]`; only the first annotation is inspected, and a callable that accepts both one and two positional arguments without it gets the request-only form. `AnyAnswerer[DepsT]` annotates a stored callback that may use either.

The context is a closed channel rather than payload[^pydantic-ask-user-docs]: `ctx.deps`, `ctx.model` and `ctx.messages` belong to the run that called the tool — for a delegated agent that is the **child's** run, not the parent's — the messages include the asking model response and its thinking parts, and `ctx.tool_call_id` is the question's call; the history is to be treated as read-only. None of it is serialized into `AskUserRequest`, its events or the deferred calls, and with `answerer=None` no answerer runs at all, so a deferred host supplies context from its own state. Durable execution may restrict which fields an answerer can read; the source defers to Temporal's run-context rules rather than naming the restriction.

The request carries `questions` and an `id` that distinguishes concurrent or repeated calls so a UI can match a reply. A valid `AskUserResponse` holds one `AskUserAnswer` per question keyed by `header`, with `selected` holding one label (or several only on a `multi_select` question), at least one either way and no duplicates — or `custom_answer='…'` with `selected` empty, whose length is unlimited so a client-supplied string must be capped by the answerer[^pydantic-ask-user-docs] A response that does not fit the request — unknown header, unoffered label, several labels on a single-select question, a missing answer — is an answerer **bug** and raises `ValueError`, which fails the run; `check_response` is exported so an answerer can validate before returning. Declining is not an error: `AskUserResponse(cancelled=True)` tells the model the user declined and nothing is raised.

Two ordering facts follow from the loop[^pydantic-ask-user-docs]: two `ask_user_question` calls in one model response reach the answerer **one at a time, after** the response's other tool calls have finished, because an answer shapes the model's *next* response rather than calls it already made.

## Notes: attaching content to an answer

`AskUserAnswer.note` takes a tuple of `UserContent` so an answer can carry an explanation or a screenshot[^pydantic-ask-user-docs] The rules are tighter than they look:

- Text and images keep their order, notes never replace the required answer, and a non-empty note must contain nonblank text or an attachment.
- File URLs must be HTTP(S) with `force_download=False`; other schemes, forced downloads, Google Files API URLs and `UploadedFile` provider references are rejected — the application should authorize access and supply `BinaryContent` instead.
- Only the rendered text of `TextContent` and `StructuredContent` is forwarded; user-supplied text metadata is dropped so a note cannot claim framework provenance.
- With notes the tool returns a `ToolReturn` whose `return_value` is the unchanged answer dictionary and whose `content` sends the notes as `UserPromptPart` content, each framed by `<answer_note header="…">`/`</answer_note>` with headers and tags inside text escaped. The boundary items carry `origin='user.pydantic-ai-harness.ask_user.answer_note.v1'`, `request_id` and `header` in metadata, so an application can identify the record without matching visible text, and the user-content origin keeps notes classified as user turns during compaction.
- The harness sets **no note size limit**, so text and attachments coming from a client must be bounded by the answerer.

Annotate the tool result as `AskUserResult` — `ToolReturn[dict[str, list[str]]] | dict[str, list[str]] | str` — and narrow with `isinstance(result, ToolReturn)` before reading `return_value`; a deferred host passes the same value into `DeferredToolResults.calls`[^pydantic-ask-user-docs]

## Waiting, timing out, declining

The run waits for the answer, and `timeout` (seconds) bounds that wait[^pydantic-ask-user-docs] On expiry — or on a resume token resolved with a failure instead of an answer — `AskUserAnsweredEvent` fires with `timed_out=True` and a cancelled response, and the model is told the user did not answer in time (the `TIMED_OUT` sentence) and continues. The parameter must be positive and defaults to `None`, which waits indefinitely[^pydantic-ask-user-docs]

In process the timeout **cancels** an answerer still running, so the answerer must be cancellable. A thread cannot be cancelled: blocking work belongs in `anyio.to_thread.run_sync(..., abandon_on_cancel=True)`, or the run waits for the thread and then uses its late answer — and a terminal answerer should read input with an async prompt library, since `input()` inside a thread would consume the next line the user types[^pydantic-ask-user-docs]

## Deferring instead of waiting

A web server or durable worker often cannot hold a run open while a person decides, so `answerer=None` defers every call: the run **ends** with `DeferredToolRequests` output, which means your `output_type` must include it, and the answer arrives in a later run[^pydantic-ask-user-docs] The three pieces that make resumption work are:

- `AskUserRequest.from_tool_call(call)` rebuilds the validated request from a pending call, keeping the `tool_call_id` as its `id` — the same id `AskUserRequestedEvent` carried before the pause — and raises `ValueError` when the call belongs to another tool;
- `ask_user_result(request, response)` validates the response like an answerer's and renders the tool result the model would have got inline, passed in `DeferredToolResults.calls` under the call's id;
- no `AskUserAnsweredEvent` fires for a deferred call, because the answer comes from you in the next run.

Persist the paused run's `all_messages()` with its pending questions, and resume with `agent.run(message_history=…, deferred_tool_results=…)`. `timeout` needs an answerer to bound, so combining it with `answerer=None` raises `UserError`.

## Durable runs and the token form

Every question is already a **deferred tool call** marked as a question — the tool raises `CallDeferred(kind='question')`, so `DeferredToolRequests.kind()` reports `'question'` — and `AskUser` answers its own questions in its `handle_deferred_tool_calls` hook, one at a time, by calling the answerer through `wait_for_external_event`, the same wait a resume-token handler uses[^pydantic-ask-user-docs] That single mechanism gives four different behaviours:

- In a plain run, the answerer is called in process.
- On **AWS Lambda durable functions**, the answerer runs in a step that records its response, so a replay does not ask again — and therefore it must return quickly; a person who may take a while should answer through the token form instead.
- On **Temporal, DBOS, Prefect and other engines without support for waiting**, the engine **refuses** the wait with a `UserError`. The source gives the reason in three steps: an in-process wait would not be recorded, so a replay would ask again, could get a different answer than the run already acted on and diverge from the engine's history, and a restart would lose the wait.
- With a **token** answerer (`TokenAnswerer`), the answerer may hand the token on — in a Slack message, say — and return `None`; the answer then arrives when your code resolves the token with the JSON form of an `AskUserResponse`, in process through `resolve_external_event` or through the engine's API such as Lambda's `SendDurableExecutionCallbackSuccess`.

Ordering is the subtle part: `get_ordering()` makes `AskUser` answer **its own** questions before a `HandleDeferredToolCalls` handler sees the remaining calls, wherever it is listed, because a generic handler that fills every call would otherwise answer the question itself and the answerer would never be asked; a handler that takes a resume token is innermost and comes later still[^pydantic-ask-user-docs] The answer passes the tool's `after_tool_execute` hooks — result guards included — as it did when the tool waited. To handle every pending call in one place instead, pass `answerer=None` and answer through `HandleDeferredToolCalls`.

## Observing the exchange

Two capability events dispatch **immediately**, so a "waiting for you" indicator starts and ends in step with the run[^pydantic-ask-user-docs]:

| Event | When | Fields |
| --- | --- | --- |
| `AskUserRequestedEvent` | Before the answerer is called, or before a deferred call pauses the run | `request` |
| `AskUserAnsweredEvent` | After the answerer returns, times out, raises, or its token resolves or fails — before the response is checked or the model sees it | `request_id`, `response`, `timed_out`, `failed` |

When the answerer raises, or a token resolves with something that is not an `AskUserResponse`, the answered event carries `failed=True` and a cancelled response, and then a `ModelRetry` from the answerer sends the model a retry prompt while any other error fails the run. A run cancelled while the answerer waits emits **no** answered event, so waiting state must also be cleared when the run ends.

`AskUser` emits no spans: the core tool-call span records the questions as arguments, and the events carry what was asked and answered[^pydantic-ask-user-docs] Answers, custom text, notes and attachments appear in the following model request's tool result and user content, so `include_content=False` is what keeps them out of traces.

`AskUser` declares the default `id` `'ask_user'`, which keys its instructions so they can be addressed and lets `defer_loading=True` work without one; two instances sharing it merge when they agree and raise `UserError` at construction when they differ, while two that must coexist need distinct ids under `PrefixTools` — or, better, one answerer that dispatches to several UIs[^pydantic-ask-user-docs] `Agent.from_spec` **cannot** construct it, because the answerer is a live object a spec has no way to name.

Alongside those classes the module exports the pieces a host wires by hand: `TOOL_NAME`, `DECLINED`, `TIMED_OUT` and `MAX_QUESTIONS` as the tool name, the two fixed result sentences and the ten-question bound; `check_response` and `ask_user_result` for validating and rendering outside an answerer; the three protocols with the `AnyAnswerer` union; and `AskUserToolset` with `ASK_USER_EVENTS`, the toolset `AskUser` registers and the namespace of its two events[^pydantic-ask-user-docs]

## Coverage and limits

The package is the single `index.md` capture with no attachments, includes or supporting files; the flow diagram and the example answerer were read in their text forms[^pydantic-ask-user-docs] External links — CLAI's terminal menu, Code Puppy, deferred tools, the Lambda approvals and Temporal run-context pages, `PrefixTools` and the Logfire content-exclusion page — were read as links and not followed. The page names no version, date, author or licence, so the concept is `draft` under the `pydantic-ai` domain rule; its examples pin `anthropic:claude-fable-5-2`, an alias no release pin corroborates.

Nothing was installed, no question asked, no answerer invoked, timed out or cancelled, no token resolved and no event received, so every claim is **Reported** and none **Observed** or **Reproduced**. The source does not state what happens to the deferred call when a resume token is never resolved, how large a note may grow before the provider rejects the request, or whether `custom_answer` text is rendered anywhere the terminal-injection rules no longer apply.

## Relationships

- **Waits on a person synchronously**, where [deferred tool approval](pydantic-ai-deferred-approvals.md) and [handling deferred tool calls](pydantic-ai-realtime-voice.md) pause the run and resume it elsewhere.
- **Depends on** the [lifecycle hooks](pydantic-ai-lifecycle-hooks.md) and capability-event machinery for its two events, and on [durable execution](pydantic-ai-durable-execution.md) for how a recorded wait behaves per engine.
- **Complements** [background tools](pydantic-ai-harness-background-tools.md): a long job runs while the model works, but a decision needs this capability's round trip.
- **Often paired with** [Coder](pydantic-ai-harness-coder.md)'s `autonomy='low'`, which puts a plan in front of the user through the model's own output rather than through questions.

[^pydantic-ask-user-docs]: Pydantic Docs, "Ask User", <https://pydantic.dev/docs/ai/harness/ask-user/>; local capture `raw/harness/ask-user/index.md`, content digest sha256:4ac2bacc, 4,095 words as declared (4,195 by `wc -w`), 574 lines, no publication date, author, licence or Pydantic AI/Harness version. Locators are line ranges in that capture: 11 for the one-line purpose; 13–35 for the flow diagram (model → `ask_user_question` → validation → answerer or `DeferredToolRequests`); 37–56 for the tool contract, the absent default answerer and the `pick_first` example; 58–92 for the `Answerer` protocol, the three signatures, the `AskUserRequest`/`AskUserResponse` shapes, `check_response`, the decline path and the injection warning; 94–112 for the context form and the two-argument annotation rule; 114–130 for `note` and its URL and provenance restrictions; 132–142 for the `AskUserResult`/`ToolReturn` shape and the `<answer_note>` framing; 144–158 for `timeout`, cancellation and the thread caveat; 160–186 for `answerer=None`, `from_tool_call`, `ask_user_result` and the paused-run resume; 188–200 for the two events, the `failed` path and the no-event-on-cancel rule; 202–226 for the question schema table, the control-character rejection and the frozen questions; 228–240 for the `TIMED_OUT` sentence, the added instruction and the `id` merge rule; 242–252 for tracing and `include_content`; 254–256 for the agent-spec limitation; 258–266 for the module-level exports; 268–318 for `AskUser`'s `answerer`, `timeout` and `id` attributes with their defaults; 320–393 for `combine`, `get_instructions`, `get_ordering`, `get_toolset` and `handle_deferred_tool_calls`; 395–478 for the three protocols and the `AnyAnswerer` union; 480–510 for `AskUserRequest.from_tool_call` and its `ValueError`; 512–560 for the response, answer and `AskUserResult` types; 562–573 for the two events' `timed_out` and `failed` attributes. Evidence class: **Reported** — vendor documentation for its own package, with no execution behind it.
