---
type: Concept
title: Pydantic AI streamed output
description: How Pydantic AI streams text and validated partial structured output — stream_text, stream_output and stream_response, the debounce and partial-validation rules, the partial_output flag, and the four cancellation surfaces.
tags: [pydantic-ai, agents, streaming, structured-output]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:10:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-output
    resource: ../raw/core-concepts/output/index.md
    scope: ../raw/core-concepts/output/
    kind: documentation
    revision: sha256:c70422e8bdd3e28400b6ca8c611c3097e9f9dc1a39a9328fc36e440fa3e1193f
    title: "Output"
---

**Reported, Pydantic AI version unspecified:** `agent.run_stream()` is an async context manager over a `StreamedRunResult`, and that result offers three ways to consume a run in progress — cumulative text, an accumulated **validated** output snapshot, or raw `ModelResponse` objects the caller validates itself. The design answers two problems the documentation names: validating a structured response before it is complete, which relies on Pydantic's partial validation added in [pydantic/pydantic#10748](https://github.com/pydantic/pydantic/pull/10748), and not knowing whether a response is a tool call or a final output until it has been peeked at. Pydantic AI streams just enough to tell, then either calls tools or hands back the stream.[^pydantic-docs-output]

Streaming works on the standard `Agent` with no special setup, and the docs state every model currently supports it.[^pydantic-docs-output]

## Streaming text

`stream_text()` yields a running string rather than a chunk: each item is the complete response so far, extended as more arrives, so a UI can re-render from the last value without accumulating deltas itself. `delta=True` yields only the new parts instead, and the method raises if the response is not text.[^pydantic-docs-output]

```python
async with agent.run_stream('Where does "hello world" come from?') as result:
    async for message in result.stream_text():
        print(message)
        #> The first known
        #> The first known use of "hello,
        #> The first known use of "hello, world" was in a 1974 textbook
```

`debounce_by` groups incoming chunks before yielding: the default `0.1` waits up to a tenth of a second, and `None` yields as soon as each chunk arrives. The docs recommend debouncing for long structured responses, where it cuts the cost of validating every chunk.[^pydantic-docs-output]

## Streaming structured output

`stream_output()` applies **partial validation** to each snapshot and full validation to the final output, so every value it yields is a complete, legal value of the output type as far as the data received allows. The docs' `UserProfile` sample shows the consequence: `{'name': 'Ben'}` appears before `dob` and `bio` are known, and an incomplete field or list item is simply **absent** until enough data has arrived for it to validate. Each yield is an accumulated snapshot, not a delta, so the right renderer replaces its value instead of appending every yield.[^pydantic-docs-output]

Because `output_type` uses [tool output](pydantic-ai-structured-output.md) by default, structured streaming needs a model that streams tool arguments. For models that do not, the docs point at Native Output or Prompted Output — Native Output with Gemini 3, and Prompted Output with earlier Gemini models that also use function tools.[^pydantic-docs-output]

Three routes exist, in increasing order of control:[^pydantic-docs-output]

| Route | What it yields | Use when |
| --- | --- | --- |
| `result.stream_output()` | Validated accumulated output snapshots | The final value is all the caller needs |
| `agent.iter()` + `node.stream(run.ctx)` | `AgentStreamEvent`s, switching to `stream_output()` at `FinalResultEvent` | Intermediate model requests and tool calls must surface too |
| `result.stream_response()` + `result.validate_response_output(...)` | Raw `ModelResponse` objects, validated by the caller | Validation itself must be controlled per snapshot |

The `iter()` route is the documented way to keep events **and** validated output: iterate each `AgentStream` until a `FinalResultEvent` appears, then consume `stream.stream_output()`, and handle call-tools nodes in the same loop for their events. One caveat comes with it — `AgentStream` is a single iterator, so once `stream_output()` takes over it consumes the remaining final-output events while validating them and those raw events never reach the preceding loop. Retaining every raw event means `run_stream_events()` and reconstructing the output yourself.[^pydantic-docs-output]

The manual route pairs `stream_response(debounce_by=0.01)` with `validate_response_output(message, allow_partial=message.state == 'incomplete')`: iterating `stream_response` cannot fail with a `ValidationError`, because the caller catches it and skips the snapshot, and `allow_partial=True` enables Pydantic's `experimental_allow_partial` flag on `TypeAdapter`.[^pydantic-docs-output]

### Output functions and validators run more than once

Streaming changes the contract of every output-side callable: when a run streams, output functions and output validators are called **once per partial output and once for the final complete output**.[^pydantic-docs-output]

`RunContext.partial_output` is the discriminator — `True` on each partial output, `False` on the final one, and always `False` for every non-streaming run method, where the callable runs once. The docs give two opposite uses:[^pydantic-docs-output]

- **Output functions with side effects** must skip them while `partial_output` is true. The `save_to_database` sample returns the record early on a partial output and only prints the database write for the final one.
- **Output validators that want to validate only the complete result** return early while `partial_output` is true, so an intermediate `'Once upon a'` is not rejected for being shorter than fifty characters.

A structured output type streamed through an output function must also tolerate partial data — the sample makes `value: int | None = None` optional for exactly that reason — and a structured `output_type` streamed through tool output depends on the model streaming tool arguments.[^pydantic-docs-output]

Streaming also changes the [end-strategy](pydantic-ai-structured-output.md) rule: under `'graceful'` and `'exhaustive'` a failing function tool would normally veto a successful output, but while streaming the first matching output is committed immediately.[^pydantic-docs-output]

## Cancelling a stream

Four surfaces stop work at different scopes, and the docs distinguish stopping generation from stopping consumption:[^pydantic-docs-output]

| Surface | Scope | Effect |
| --- | --- | --- |
| `StreamedRunResult.cancel()` | The current model response | Asks the provider to stop generating tokens and closes the HTTP connection where the integration supports it; `result.cancelled` turns true and the final `ModelResponse` is marked `state='interrupted'` |
| `AgentStream.cancel()` | The model request inside an `agent.iter()` node | Cancels that request's stream |
| `AgentRunEvents.cancel()` | The whole run started by `run_stream_events()` | Cancels the run; continued iteration then raises `RunCancelled` |
| `RunContext.cancel()` | The whole run, called from a tool or `event_stream_handler` | The in-run equivalent of the above |

`run_stream()` and `iter()` cancel by closing the underlying model stream, and `run_stream_events()` is itself an async context manager, so leaving the `async with` block cancels the background run task deterministically — `break`ing out of the loop while a `FinalResultEvent` is a fine way to stop, and cleanup happens as the context exits. The distinction the docs draw is that this cleans up local consumption, while `cancel()` is what stops generation **immediately**. The `AgentRunEvents` handle also exposes `all_messages()`, `new_messages()`, `usage` and the completed `result`.[^pydantic-docs-output]

Cancelling a non-streaming run is a separate mechanism, and bounding a single step's duration is another; both belong to the agent and timeout surfaces rather than to this one.[^pydantic-docs-output]

## Evidence and coverage

The sole artifact is the Pydantic documentation capture `index.md` (8,218 words as declared), inspected as text, with no attachments, includes, downloads or supporting files. It names no Pydantic AI version, author, publication date or licence, and its samples pin model names (`google:gemini-3.8-flash`, `openai:gpt-6.1-sol`) that no other capture here corroborates. The API pages this section leans on — `Agent.run_stream`, `run_stream_events`, `AgentRunEvents`, `AgentStream`, `StreamedRunResult.stream_text`/`stream_output`/`stream_response`/`validate_response_output`/`cancel`, `RunContext.cancel` and `RunContext.partial_output` — and the linked Example pages (stream markdown, stream whales) were read as links, not followed, so the exact signatures, event classes and provider-level cancellation support are unverified. Nothing was installed, no agent streamed, no `FinalResultEvent` observed and no stream cancelled, so every claim is **Reported**; the event classes the docs name (`AgentStreamEvent`, `FinalResultEvent`, `PartStartEvent`, `AgentRunEvents`) are described but never enumerated, so what else a caller can observe on a stream is a limit of this page. The page is `draft` under the `pydantic-ai` domain rule and carries `stale_after` because streaming APIs and per-provider streaming support are release-sensitive.

## Relationships

- **Depends on** [Pydantic AI structured output](pydantic-ai-structured-output.md): the streamed value is a snapshot of the same `output_type` schema, and the default tool-output mode is what makes structured streaming depend on streamed tool arguments.
- **Uses** [models and providers](pydantic-ai-models-and-providers.md): streaming support and streamed tool arguments are model capabilities, which is why some models need Native or Prompted Output.
- **Shapes** [Pydantic AI conversation state](pydantic-ai-conversation-state.md): a run cancelled mid-response ends with an `interrupted` response whose messages are the ones state and history keep.
- **Delivers citations late**, per [Pydantic AI citations](pydantic-ai-citations.md): a citation can arrive after the text it supports — at the end of each text part on Anthropic, Bedrock and OpenAI Responses, and only at the end of the response on Google and OpenAI Chat — so the final response, not the part stream, is the complete citation source.
- **See also** [Pydantic AI output truncation](pydantic-ai-output-truncation.md): a stream cut off by the token limit surfaces the same `OutputTokenLimitExceeded` and `IncompleteToolCall` errors as a non-streaming run.

[^pydantic-docs-output]: Pydantic Docs, "Output" (`https://pydantic.dev/docs/ai/core-concepts/output/`, 8,218 words as declared); local capture `raw/core-concepts/output/index.md`, content digest sha256:c70422e8. "Streamed Results" (lines 873–879) for the two streaming challenges, partial validation and the sniffing step; "Streaming Text" (lines 880–937) for `run_stream`, the context-manager lifetime, cumulative `stream_text`, `delta=True`, `debounce_by` at `0.1` and `None`; "Streaming Structured Output" (lines 938–1081) for `stream_output` partial-then-full validation, absent incomplete fields, the accumulated-snapshot rule, the model-support caveat and Native/Prompted alternatives, the `iter()`/`AgentStreamEvent`/`FinalResultEvent` pattern, the single-iterator caveat and `run_stream_events`, and `stream_response` with `validate_response_output` and `experimental_allow_partial`; "Handling partial output in output functions" (lines 263–304) and "Handling partial output in output validators" (lines 725–763) for the repeated calls, `partial_output` semantics and the two samples; "Tool calls alongside a final result" (lines 433–458) for the streaming exemption from the function-tool veto; "Cancelling Streams" (lines 1082–1177) for the four cancellation surfaces, `cancelled`, `state='interrupted'`, the `async with` cleanup rule and the `AgentRunEvents` handle. Excerpted samples were read, not executed. Evidence class: **Reported** — vendor documentation naming no release version.
