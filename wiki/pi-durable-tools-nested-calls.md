---
type: Concept
title: Pi Durable Tools and Nested Calls
description: How pi-durable defines tools, routes output to models versus programs, replays interrupted calls, restricts callers, runs nested tool calls as owned tasks, and handles images and bash results.
tags: [pi-durable, tools, replay, subagents]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T16:07:19Z }
stale_after: 2027-01-25
sources:
  - id: pi-durable-readme
    resource: ../raw/pi-durable-readme.md
    kind: docs
    title: "@earendil-works/pi-durable README"
  - id: tannermidd-durable
    resource: ../raw/tannermidd-durable/index.md
    scope: ../raw/tannermidd-durable/
    kind: article
    title: "Pi Durable, explained (Pi Pocket guide)"
---

Tools in pi-durable are defined with `defineTool`, validated against a TypeBox schema, and executed as their own durable tasks. The call's intent is committed before `execute()` runs; if the process dies mid-call, the tool reruns on reopen only when it is declared `replay: "safe"`, otherwise the model gets an `interrupted` error result with the output committed so far. The guide treats `"unsafe"` as the default: its simulator leaves `read` at that default and must opt `bash` into `"safe"` to see it rerun.[^tannermidd-durable] Throwing from `execute()` yields an error result, and a result can carry `usage` (added to conversation usage) or `control: { terminate: true }` (when every result of the round asks for it, the run ends without another model request).[^pi-durable-readme]

## Result channels

| Channel | Audience | Behavior |
| --- | --- | --- |
| `output` | The model | `api.output()` streams running output, which becomes the result when `execute()` returns no `output`. |
| `structuredOutput` | Programs calling the tool | A tool declaring `structuredOutputSchema` must return a matching value, which the Harness validates. |
| `details` | UIs | Stored alongside `output`; the transcript stores only `output` and `details`. |

A schema-less tool's program-facing result is bounded: one text item becomes a string, one image its `ImageContent`, nothing becomes `""`, and anything else the content list, errors included. `structuredOutput` is always the tool's own value: a schema tool's error result keeps the value it returned, while the text of a schema-less tool's error is placed in a `tool_error` diagnostic. A missing, undeclared, or invalid `structuredOutput` turns a nested call into an `invalid_structured_output` error; for a model call, which never sees it, it is dropped and reported through `onReport`. Error results the Harness writes itself (blocked, invalid, interrupted, aborted) carry no `structuredOutput`, and their `diagnostics` say what went wrong. An `afterTool` hook that redacts a schema tool's `output` must redact its `structuredOutput` too.[^pi-durable-readme]

## Who may call a tool

`callers` selects the model, other tools through `executeTool()`, or both (the default). A conversation's `modelTools` narrows which tools the model is offered without taking them away from tools, while `tools` still decides what is enabled at all; `modelTools` cannot add to it. `conversation.agent()` resolves both lists as `tools` (offered to the model) and `callable` (resolved by nested calls).[^pi-durable-readme]

A `deferred: true` tool is not offered to the model until loaded, though other tools can call it any time. The `tool_search` extension (`createToolSearchExtension()`) lets the model search deferred tools and loads matches with `control.addTools`, recorded in `modelTools`; loaded tools stay offered on that branch, including after compaction, and the `codemode` section leaves deferred tools out. Deferred tools suit large tool sets such as an MCP server's.[^pi-durable-readme]

## Nested calls

`api.executeTool()` runs another tool as a nested call, as code mode scripts and MCP bridges do. The nested call is its own tool task owned by the caller: it is validated, runs `ToolTask` hooks, keeps its own output limits and replay policy, and returns its result to the caller instead of the transcript.[^pi-durable-readme]

- The caller receives the nested call's `taskId`, `structuredOutput`, `details`, `diagnostics`, `usage`, and `isError`, never the model-facing `output`. A blocked, invalid, failed, or aborted nested call returns an `isError` result.
- `executeTool()` rejects once `execute()` has returned, when the caller is aborted, or when the Harness closes; cancelling its context stops only the wait.
- Hooks see the nested call's `call.parent`, so a guard can treat script-initiated calls differently.
- While the caller runs, nested calls appear in `pi.live.nestedTools` with their arguments and a summary (error, duration, usage), and as tool events with `parentToolCallId` and `parentTaskId`; `progress: false` keeps their running output out of `pi.live`. Before the caller settles, leftover nested calls are aborted, including those from an earlier attempt.
- Each nested call has a key: its position among the caller's nested calls unless the caller passes `{ key }`. A replay-safe caller that reruns and calls in the same order (or with the same keys) gets the finished or still-running calls back instead of starting them again. A nested call interrupted before its result was committed follows its own replay policy, so a replay-safe tool with external effects still needs its own idempotency. A caller that is not replay-safe never reruns, so after a restart its unfinished nested calls are abandoned with everything they own.
- A nested call's `usage` is counted under its own tool; passing it on in the caller's result counts it twice.
- Nested results are not kept long: they live in the caller's task documents (`NestedCallDoc`, one per key, holding `{ taskId, result? }`) until the caller settles, while the nested task record keeps a small receipt. A stored result is exactly what `executeTool()` returns, so an image or bash tail is stored once.
- Nothing bounds nesting depth; a tool with the default `callers` can even call itself. Restrict `callers`, and use `abandonOnRestart` for work that must not outlive its creator.

[^pi-durable-readme]

## Coding tools and images

`@earendil-works/pi-durable/tools` provides `read`, `write`, `edit`, `bash`, and the `CodingTools` extension with all four. They touch files and processes only through the call's environment (see [extensions and environments](pi-durable-extensions-hooks-agents.md)).[^pi-durable-readme]

`read` returns an image file as one image block (`ImageContent` for programs), limited by the model's `inputLimits.images.resize` (default 2000x2000 pixels and 4.5 MB of base64). Without an image processor it sends in-limit PNG, JPEG, GIF, and WebP files as they are, reading dimensions from the header, and refuses larger or other formats. With a processor it decodes every image, uprights it by EXIF orientation, converts BMP to PNG, and shrinks it to fit. The Photon-based processor runs on WebAssembly and is loaded only when imported (`/images/node`, `/images/cloudflare`, or `createPhotonImages(wasm)`); `/images/node` works in a worker thread that exits after 30 s without images, while elsewhere decoding takes the image's full size in WebAssembly memory that does not shrink again, so memory-constrained hosts such as Cloudflare Workers should leave it out unless images stay small. A model without image input sees a placeholder and `read` says so in a diagnostic.[^pi-durable-readme]

A later extension's same-name tool replaces an earlier one where both are selected, and `wrapTool()` decorates whichever tool won. The built-in `bash` returns `{ output, truncated, fullOutputPath?, exitCode }`, where `output` is the retained tail the model sees and can be read with `api.retainedOutput()`; a nonzero exit is an error result that still carries it.[^pi-durable-readme]

## Evidence and limits

All tool semantics are **Reported** documentation; no tool was executed, and image limits/processor behavior were not tested. The replay default is reported by the secondary guide rather than stated in the README excerpt compiled here. The README does not state which model providers were verified for `structuredOutput` handling.

## Relationships

- **Runs as** [durable tasks](pi-durable-tasks.md), one per call and per nested call.
- **Is wrapped and guarded by** [extensions and hooks](pi-durable-extensions-hooks-agents.md), and resolves the conversation's [agent](pi-durable-conversations.md) at each phase.
- **Is invoked by** [code mode](pi-durable-code-mode.md) scripts as nested calls with a replay journal.
- **Is constrained by** the application-level [replay safety](pi-durable-replay-safety.md) decision for effectful tools.
- **Reports** calls and nested calls through [observability](pi-durable-observability-telemetry.md).
- **Uses** the environment built per call and the [storage](pi-durable-storage.md) commit path.

[^pi-durable-readme]: @earendil-works/pi-durable README (`raw/pi-durable-readme.md`), locators: §Tools, §Calling tools from tools, §Who may call a tool, §Tasks a restart abandons.

[^tannermidd-durable]: Pi Pocket, “Pi Durable, explained” (`raw/tannermidd-durable/index.md`), locators: §Stop the process during an answer.
