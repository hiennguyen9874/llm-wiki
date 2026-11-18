---
type: Concept
title: Pydantic AI capability parts and authority
description: How a Pydantic AI capability declares typed content it inserts mid-conversation — part kinds with tags, notes and attributes, the source-to-authority table and its ceiling, what a downgrade renders, how parts survive storage, and the framing helpers for text that is not a part.
tags: [pydantic-ai, capabilities, context-management, security]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:20:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-custom-capabilities
    resource: ../raw/capabilities/custom/index.md
    scope: ../raw/capabilities/custom/
    kind: documentation
    revision: sha256:8266876f368fff0ff3cccd0d01daa125794d6d17a79ba31ecaeb85278603fe84
    title: "Building Custom Capabilities"
---

A capability that wants to tell the model something partway through a conversation — a sub-agent's report, a reviewer's feedback, the budget left — does not build a tag or pick a voice: it defines a **capability part kind** and hands instances to `ctx.enqueue`, and Pydantic AI renders each one before any model sees the history[^pydantic-docs-custom-capabilities] The declared class carries two independent decisions — what the content *is* (its tag, attributes and note) and who wrote it (its source, capped by the capability's own authority) — and the rendering the model receives is the lower of the two. This page covers the declaration and attribution side; how content enters a live run, what position and priority it lands at, and how a request-scoped prompt reaches each provider belong to [mid-run injection](pydantic-ai-mid-run-injection.md), while the framework's own tags and lookalike notes belong to [prompt framing](pydantic-ai-prompt-framing.md).

## Declaring a kind

Two base classes split the channel[^pydantic-docs-custom-capabilities]:

| Base class | For | Reaches the model as |
| --- | --- | --- |
| `DataCapabilityPart` | Data the capability inserts: a state update, a memory snapshot, a late tool result | A tag on the user channel, inside the frame its kind declares |
| `InstructionCapabilityPart` | An instruction in the application's own words | A mid-conversation system message |

The class arguments declare the kind and, for a data kind, how its content is tagged[^pydantic-docs-custom-capabilities]:

| Argument | Effect |
| --- | --- |
| `namespace`, `name` | Make up the part's `kind`, `namespace.name`, which identifies it when history is stored and loaded. `name` defaults to the class name in snake_case without a `Part` suffix, subclasses inherit the namespace, both must be lowercase snake_case, and a kind can be defined only once |
| `tag` | Data kinds only, and required there: the lowercase snake_case tag the content goes in. Prefer an existing tag that says what the content *is*, such as `tool_result`; system-voice tags such as `system`, names ending in `_diff` and the reserved `pyai:` prefix are refused |
| `attributes` | Data kinds only: the typed fields whose values go on the tag, in that order, strings or integers, left off when `None`. Keep them to identity and outcome, such as whose output it is |
| `note` | Data kinds only: a fixed sentence in the application's voice that goes with each data part, naming its frame with `{frame}`, which renders as the tag. Name the frame, never its position, because providers order system and user content their own way |

A typed field that is not one of the `attributes` is for your code only — the model never sees it[^pydantic-docs-custom-capabilities] Two further rules matter in practice: `ctx.enqueue` stamps `capability_id` with the run id of the capability that enqueued the part, which is how parts of one kind from several instances of a capability are told apart; and subclassing `DataCapabilityPart[str]` narrows `content` to `str`, so a type checker knows it and loading history validates it, while an unparameterized data kind accepts text, `StructuredContent` or a sequence of user content such as files. Code that needs a part again finds it **by type, never by its text**[^pydantic-docs-custom-capabilities]

## What the model sees

The declaration decides the rendering; the capability never escapes text itself[^pydantic-docs-custom-capabilities] The vendor's reviewer part, with `tag='review_feedback'`, `attributes=('reviewer',)`, a `note` naming `{frame}` and `reviewer='loop_check'`, reaches the model as its note, then the tagged content:

```
The accompanying <review_feedback> is feedback from an automated reviewer about your last step.
<review_feedback reviewer="loop_check">The second search repeats the first one.</review_feedback>
```

The note is a mid-conversation system message, or a `<system>` block on a model without one, and the content goes between the tags exactly as written: nothing is escaped, a file goes in as a file, and content of more than one line starts and ends on lines of its own[^pydantic-docs-custom-capabilities] Text inside it that looks like a framework frame, or that opens or closes the part's own tag, gets a note naming who wrote it — the same treatment such text gets from a user. System voice takes a string literal or an `OperatorText`, so text your code builds says it is the operator's and a type checker rejects a plain runtime `str`.

## Source and authority

Every part declares where its content came from, which decides how much authority it carries[^pydantic-docs-custom-capabilities]:

| Source | Authority |
| --- | --- |
| `OperatorSource()` — your code or configuration wrote it | `'operator'` |
| `WorkspaceSource.from_workspace(workspace, path)` — read from a workspace file, asking the workspace for its files' authority; no other way to build one | The workspace's `authority`: `'operator'` unless an `AuthorityWorkspace` lowers it |
| `UserSource()` — the user wrote it, such as a prompt they saved earlier | `'user'` |
| `ToolResultSource(tool_name=...)` — a tool's output | `'none'` |
| `ModelSource(author)` — a model wrote it, such as a judge or sub-agent | `'none'` |
| `CapabilitySource(capability_id, authority=...)` — substituted by `ctx.enqueue` for a source with more authority than the capability's ceiling | The capability's ceiling |

A part reaches the model with the **lower** of its source's authority and the authority its kind asks for — an instruction kind asks for `'operator'`, a data kind for `'none'`. A source with less authority than the kind asks for downgrades the part instead of being refused[^pydantic-docs-custom-capabilities]:

- `'operator'`: the content is a system message in the application's voice. Only an instruction part from an operator-level source gets there.
- `'user'`: the content goes in a tag on the user channel, with a note in the application's voice saying the application attached it on the user's behalf.
- `'none'`: the content goes in a tag on the user channel, with a note naming who wrote it — "the `fetch` tool", "the trajectory judge" — and saying it is not the user's or the application's. An instruction part's tag is its kind's name, which is why that name has to work as a tag.

A note qualifies content and never vouches for it: a data kind's own note is followed by who wrote the content whenever that is not the operator[^pydantic-docs-custom-capabilities] Instruction content is a string literal or an `OperatorText`. `OperatorText.from_workspace` is the only `OperatorText` that carries the workspace's source, so text read from a workspace the operator does not control is downgraded whatever source the part is given; `OperatorText(text.strip())` is a new claim that the operator wrote it, so changing the text means passing `WorkspaceSource.from_workspace(workspace, path)` as the part's source too. Enqueueing a part that would put something resembling a framework frame — a `<system>` tag — in the application's voice raises `UserError`, and a capability with fixed text in the application's voice checks it when it is set up.

## The ceiling

A capability's `authority` attribute caps the authority of everything it enqueues, `'operator'` by default, and it only ever lowers[^pydantic-docs-custom-capabilities] Set it on a capability whose mid-conversation content you do not fully control, such as one loaded from a plugin; `with_authority()` returns a lowered copy, so one instance of a reviewer can be framed as data while another in the same agent is not. `with_authority('operator')` on a class that sets `'none'` leaves it at `'none'`.

The ceiling covers what the capability sends mid-conversation wherever its code runs — a hook, a tool, `for_run`, a `DynamicCapability` factory, or a function it returns for its toolset, instructions, model settings or description[^pydantic-docs-custom-capabilities] It does **not** cap the capability's instructions, its tool names and descriptions, or its tools' return values, which reach the model as the application configured them: review or leave those out yourself, and for an MCP server you do not trust also pass `include_instructions=False`. Content the application enqueues itself, through `AgentRun.enqueue` or a `Hooks` function, keeps its voice.

Below `'operator'`, `ctx.enqueue` treats what the capability sends by kind so nothing reaches the model as the application's or the user's words[^pydantic-docs-custom-capabilities]:

| What is enqueued | Becomes |
| --- | --- |
| A capability part whose source has more authority than the ceiling | Stored with a `CapabilitySource` naming the capability and the ceiling, so history records who wrote it and with how much authority |
| A `SystemPromptPart` | An instruction part lowered to the ceiling |
| User content or a `UserPromptPart` from a capability at `'none'` | Data in a `<capability_content>` frame whose note names the capability |
| Retry feedback, which would otherwise say the application's validation failed | The capability's own text: plain user text at `'user'`, data at `'none'` |
| `ToolReturn.content` of a tool the capability contributes | `<capability_content>` data at `'none'`, rather than user text |
| A plain `ToolReturnPart` | Kept as it is: tool output is tool output whoever sends it |

Anything else raises `UserError` in `ctx.enqueue`: the framework's own records of the run's state such as an `InstructionDeltaPart`, a `CompactionPart`, a typed tool return such as a tool-search result, a `ModelResponse`, a `ModelRequest` carrying `instructions`, and a `SpeechPart` from a capability at `'none'`[^pydantic-docs-custom-capabilities]

One placement rule survives the downgrade: an instruction part with `scope='request'` still applies to its own request only. Because it now sits on the user channel, which no provider clears, it goes last in its request and the cache breakpoints Pydantic AI places on the history go ahead of it — leaving the conversation before it cached even for a capability that sends one every step[^pydantic-docs-custom-capabilities]

For a workspace capability such as `LocalWorkspace(authority=...)`, the same attribute is also the default authority of the workspace's files, and a file another capability reads through a workspace carries the workspace's level for that file, capped again by the reader's own authority; [workspace file authority](pydantic-ai-workspace-authority.md) owns the per-path resolution.

## Stored with the history

Capability parts are stored in the message history like any other part, so they round-trip through `ModelMessagesTypeAdapter` as their own class — as long as the module that defines the kind is imported before history is loaded, which is why kinds belong at module level[^pydantic-docs-custom-capabilities] A part also stores how it is rendered, so changing a kind's tag, note or attributes later changes only new parts: a conversation saved earlier keeps sending the same bytes and keeps its prompt cache. A process that does not define the kind loads the part as an `UnknownCapabilityPart`, which renders exactly as the original did and serializes back to it.

The UI adapters keep capability parts on the server: they are not sent to a frontend, and `sanitize_messages` drops one a client sends back, since a client could otherwise write one in the application's voice[^pydantic-docs-custom-capabilities] A conversation whose model should keep seeing them therefore keeps its history on the server, for example through [conversation state](pydantic-ai-conversation-state.md).

## Framing text that is not a part

Text a capability puts into prompt text outside a part — a value interpolated into instructions, or a tool's return content — can be tagged with the `pydantic_ai.framing` primitives instead[^pydantic-docs-custom-capabilities] Register a tag once at module level with `register_tag` and render with `wrap`:

```python
REVIEWER_NOTE = register_tag('reviewer_note')

def render_note(note: str, *, reviewer: str) -> str:
    return wrap(REVIEWER_NOTE, note, reviewer=reviewer)
```

`wrap` escapes registered tags in the body of any data tag you render with it, Pydantic AI's own tag names included: the `<` of every opening and closing spelling of every framing tag becomes `&lt;`, in any case, with whitespace around the `/`, with attributes, self-closing, or cut off at the end of the body[^pydantic-docs-custom-capabilities] It HTML-escapes attribute values, leaves off those that are `None`, and writes attribute names as given, so they must be lowercase snake_case — other characters raise `UserError`, while a name an earlier rule allowed such as `_ref` still works with a deprecation warning. Content that mentions no framing tag goes in exactly as written. `<system>` is the exception: its body is the application's own text and may carry data tags the framework built, so only `<system>` itself is escaped there.

Three companions cover the rest[^pydantic-docs-custom-capabilities]:

- For a body that is not a string, such as a file, put it between `open_tag` and `close_tag`, which render tags the same way but escape nothing in between.
- For untrusted text that ends up inside a frame without going through `wrap`, use `neutralize_tags`.
- `wrap`, `open_tag` and `close_tag` take data tags only and raise for `'system'`, whose voice tag Pydantic AI renders only from a `SystemPromptPart` on a model with no mid-conversation system role. Instructions you wrote belong in a `SystemPromptPart`; everything else belongs in a data tag.

Tag names are lowercase snake_case; `register_tag` raises `UserError` for any other name and for Pydantic AI's own tags — the `DataTag` values, which `wrap` takes as they are, and `'system'`[^pydantic-docs-custom-capabilities] Registering a name again returns the same tag, `wrap`/`open_tag`/`close_tag` raise for a tag that was never registered, and registering at import time is what makes every process escape identically, so the same history always renders to the same bytes. Like the framework's own framing, a tag tells the model where content came from; it does not prove it — the trust boundary is [client-supplied history](pydantic-ai-client-supplied-history.md)'s problem.

## Limits

- The capture names **no Pydantic AI version, date, author or licence**, so no API name or refusal rule here is tied to a release and the page is `draft` under the `pydantic-ai` domain rule[^pydantic-docs-custom-capabilities]
- The class arguments and authority tables are documentation prose rather than a signature reference: the `CapabilityPart` dataclass fields beyond `kind`, `source`, `capability_id`, `content`, `rendering` and `scope`, the exact error type for a duplicate kind or an unregistered class, and the full `DataTag` list are not given.
- The rendering example is one data kind and one instruction kind; the per-source note wording, whether a downgraded `SpeechPart` has a substitute channel, and how a typed tool return is meant to travel from a capability at `'none'` are stated as refusals without an alternative.
- Which model classes lack a mid-conversation system role is deferred to the prompt-framing and message-history pages, and whether a kind's identity has to be unique across a deployment or only within an import is not stated.
- Nothing was installed, no capability, part, source or tag constructed, and no history rendered, stored or reloaded, so every claim is **Reported** and none **Observed** or **Reproduced**. One reading is **Synthesis**: because the stored part keeps its rendering but its `kind` is what history loading keys on, a later rename of `namespace`/`name` should leave old parts rendering identically while loading as `UnknownCapabilityPart` rather than as their class — the source states both halves separately and never combines them.

## Relationships

- **Depends on** [capability parts and the capability primitive](pydantic-ai-capability-primitive.md): a custom capability is the thing that declares and enqueues these parts, per [custom capabilities](pydantic-ai-custom-capabilities.md).
- **Complements** [mid-run injection](pydantic-ai-mid-run-injection.md), which owns `enqueue`'s timing, priorities, placement and request-scoped rendering, and [prompt framing](pydantic-ai-prompt-framing.md), which owns the framework's own tags, its lookalike notes and its announcement.
- **Supplies the voices** described in [workspace file authority](pydantic-ai-workspace-authority.md): a capability's authority doubles as the default level of its workspace's files, and `WorkspaceSource.from_workspace` is one of the six sources here.
- **Round-trips through** [message history](pydantic-ai-message-history.md) as a typed part, and is stripped from client-supplied history by [client-supplied history](pydantic-ai-client-supplied-history.md)'s `sanitize_messages`.
- **Protects** the cached prefix described in [prompt caching](pydantic-ai-prompt-caching.md): appended instruction changes and stored rendering are what keep a saved conversation sending the same bytes.
- **Is rendered by** the framework inside `prepare_messages`, the same point [mid-run injection](pydantic-ai-mid-run-injection.md) records for typed parts, which is why a stored history is provider-neutral until it is sent.

[^pydantic-docs-custom-capabilities]: Pydantic Docs, "Building Custom Capabilities" (https://pydantic.dev/docs/ai/capabilities/custom/; 13,581 words as declared, 13,832 by local `wc -w`; language `en`; no publication date, author, licence or Pydantic AI version), §"Telling the model things mid-conversation" (raw lines 322–423) for the two base classes, the `namespace`/`name`/`tag`/`attributes`/`note` argument table and its rules, the reviewer sample and its printed `kind`, the invisible-to-the-model fields, `ctx.enqueue`'s `capability_id` stamping, the `DataCapabilityPart[str]` narrowing, and find-by-type-never-by-text; §"Where the content came from" (424–475) for the rendered note-plus-tag example, the system-message or `<system>` note placement, the content-as-written rule, the lookalike note inside a part, the six-source authority table, the kind's asked-for authority and the lower-of rule, the three rendering voices and their notes, the `OperatorText` and `WorkspaceSource.from_workspace` downgrade rules, the `UserError` for a frame-shaped application-voice part, the `authority` attribute, `with_authority()`, the ceiling's coverage and its exclusions, the six-row by-kind downgrade table, the `UserError` refusal list, the request-scoped placement and cache-breakpoint rule, the capability-as-workspace-default-authority rule, and the lookalike note for part content; §"Stored with the history" (476–483) for module-level kinds, the type-adapter round trip, the stored rendering and frozen bytes, `UnknownCapabilityPart`, the UI adapters keeping parts server-side and `sanitize_messages` dropping client-sent ones; §"Framing data in prompt text" (484–525) for `register_tag`/`wrap`, the escaping rules and attribute handling, the `_ref` deprecation, the `<system>` exception, `open_tag`/`close_tag` for non-string bodies, `neutralize_tags`, the data-tags-only restriction, tag-name validation and re-registration, and the tell-don't-prove caveat. Local capture: `raw/capabilities/custom/index.md`, content digest sha256:8266876f. Evidence class: **Reported** — vendor documentation naming no release version; no part, source or tag was constructed and no history rendered.
