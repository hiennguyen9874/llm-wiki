---
type: Concept
title: Pydantic AI workspace selection and reattachment
description: How a Pydantic AI run picks its workspace — the workspace= override, the WorkspaceRef recorded on every response, the capability fallback that follows it, the errors each path raises, and how a capability supplies its own backend.
tags: [pydantic-ai, workspaces, sandboxing, conversation-state]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:22:52Z }
stale_after: 2027-01-16
sources:
  - id: pydantic-workspace-docs
    resource: ../raw/core-concepts/workspace/index.md
    scope: ../raw/core-concepts/workspace/
    kind: documentation
    revision: sha256:106c823ceb0c9563c3569f0dc7dac59f8a7e88365b54f2dc10bc3c3df5c09871
    title: "Workspaces"
---

A run gets exactly one workspace, chosen by a three-step precedence rather than by a global setting: the `workspace=` argument, else the reference recorded on the latest response in `message_history`, else the agent's own workspace capabilities. The reference is part of the message history — a small `WorkspaceRef` dataclass of `provider` and `id` on `ModelResponse.workspace_ref` — so continuing a conversation in the same sandbox is a property of the stored messages, and every later run either reaches that environment, refuses, or starts a new one on request[^pydantic-workspace-docs]

## Precedence

A run takes its workspace from the first of these that applies[^pydantic-workspace-docs]:

1. The `workspace=` argument to the run.
2. The reference on the latest response in `message_history`.
3. The agent's workspace capabilities — its directory for `LocalWorkspace`, a new sandbox for a sandbox provider.

`workspace=` itself accepts three forms: `'new'` to start a fresh environment and ignore the one in history; a `WorkspaceRef`, such as a saved `result.workspace.ref`, for the agent's capabilities to attach to; or a workspace or backend used as is — `result.workspace`, `ctx.workspace`, or a backend such as `LocalWorkspaceBackend('/tmp/scratch')`[^pydantic-workspace-docs]

## Continuing in the same environment

Passing the history is enough. With a sandbox, the files and installed packages from the first run are still there, because each model response records the workspace it ran in[^pydantic-workspace-docs]:

```python
first = await agent.run('Write fizzbuzz to fizzbuzz.py and run it.')
await agent.run('Now add a test for it.', message_history=first.all_messages())
```

That survives serialization: `first.response.workspace_ref` equals `first.workspace.ref`, and a history round-tripped through `all_messages_json()` and `ModelMessagesTypeAdapter.validate_json()` reattaches to the same environment. To continue without the history — a new conversation about the same project — save `first.workspace.ref` and pass it as `workspace=ref`[^pydantic-workspace-docs]

Three rules qualify the reference[^pydantic-workspace-docs]:

- A sandbox's `ref` is `None` until the run first uses it, so a run that never touched the workspace records no reference; a later turn that does not use it keeps the earlier reference.
- If the environment a reference names no longer exists, the run's first use of it (at run start for durable runs) raises `WorkspaceUnavailableError` instead of quietly starting over. Pass `workspace='new'` to start over on purpose.
- A run that never used its workspace records no reference, so a method call on `result.workspace` with `ref=None` afterwards can create a new sandbox that no message accounts for — check the ref and arrange cleanup for anything you create.

## Several capabilities and provider migration

An agent can hold several workspace capabilities. Those passed to the run are asked before the agent's own, each in order; with a reference, the first that recognizes it supplies the workspace, and without one, the first that returns a workspace does. That ordering is the migration path between providers: list the new capability first so new conversations use it and keep the old one so conversations that started there continue in it[^pydantic-workspace-docs]

```python
agent = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[
        LocalWorkspace('~/projects/current', id='current'),  # new conversations
        LocalWorkspace('~/projects/archive', id='archive'),  # conversations that started here
    ],
)
```

A capability only attaches to references it recognizes, which is also a containment rule: `LocalWorkspace` accepts a reference to its own directory and no other, so message history cannot point the agent at another directory on the machine. It continues only in a reference naming its configured directory exactly as written, so a reference spelled through a symlink is declined[^pydantic-workspace-docs]

## What happens when nothing supplies a workspace

| Situation | Outcome |
| --- | --- |
| A history reference exists, the agent has workspace capabilities, and none recognizes it — for example after switching providers | `UserError`; pass `workspace='new'` or keep the old capability |
| An agent with no workspace capability sees a history reference, such as a summarizer | The reference is ignored |
| `WorkspaceRef` or `workspace='new'` passed as `workspace=` and nothing supplies a workspace | `UserError` |
| No reference and no capability | The run has no workspace, and tools that use it raise `WorkspaceUnavailableError` |

For file inspection without changes, use a read-only workspace and read tools; to answer without file access at all, use a no-file-tools agent, since a workspace-backed tool needs an attached workspace and `UnavailableWorkspace` deliberately refuses every operation[^pydantic-workspace-docs]

## Deleting what a reference names

Nothing in the framework deletes an environment: a sandbox keeps running after the run until you delete it or its provider's lifetime settings stop it. A successful run returns `result.workspace.ref`, so the same reference serves for continuing the conversation or for deleting it later. A failed run returns no result, so its sandbox is deleted from an `on_run_error` hook, where `ctx.workspace.ref` names it — `after_run` does not run when a run fails. A project that deletes the sandbox after each run must pass `workspace='new'` when continuing that history, or the next run raises `WorkspaceUnavailableError` because the recorded environment is gone[^pydantic-workspace-docs]

## Client-supplied history

`sanitize_messages` and the UI adapters strip references from history a client sends you, so a client cannot choose the environment your agent works in. Save the reference on your server and pass it as `workspace=` instead[^pydantic-workspace-docs] This is the same trust boundary as [workspace file authority](pydantic-ai-workspace-authority.md), applied to the reference rather than to file text.

## Handing a workspace to another agent

`workspace=` also takes a live workspace, which is how one agent lends its environment to another. In the source's example a coding agent asks a reviewer agent to check its work: the reviewer reads the same files through `ctx.workspace.read_text`, `ReadOnlyWorkspace(ctx.workspace)` stops it from changing them, and `usage=ctx.usage` keeps the nested run on the parent's budget. The reviewer has no workspace capability of its own — it works wherever it is told to, so the same agent can review a local checkout in one run and a sandbox in the next[^pydantic-workspace-docs]

## Supplying a workspace from a capability

A capability that owns its own environments implements `get_workspace`, which the run calls with the current `ref`. The source's example points each user at their own directory named by `deps`[^pydantic-workspace-docs]:

- With `ref=None`, return the backend for a new or default environment; with a recognized `ref`, return a backend that attaches to it; return `None` for any other.
- Validate ref ids before using them as paths or identifiers, since they can arrive from stored or untrusted history.
- To apply a policy, return a `Workspace` around the backend, such as `ReadOnlyWorkspace(Workspace(backend))`.
- Do no I/O and keep no state in `get_workspace`: it can be called more than once per run, and the backend should connect on its first operation.
- A capability that supplies a workspace cannot use `defer_loading=True`, because the workspace is chosen when the run starts.

`LocalWorkspaceBackend` never creates its directory, and every operation — absolute paths included — raises `WorkspaceUnavailableError` until it exists, so a per-user capability has to create each directory when it creates the user. That separates where users start; like `LocalWorkspace`, it isolates nothing[^pydantic-workspace-docs]

A capability that *needs* a workspace can check `ctx.workspace.attached` in `before_run` and raise `UserError` naming what to attach, so the run fails at its start rather than on the first tool call[^pydantic-workspace-docs]

## Tests and the realtime gap

For tests, `with agent.override(workspace=LocalWorkspaceBackend(path)):` temporarily uses a local workspace instead of the agent's capability, the reference in history, or a per-run `workspace=`, mirroring `override(model=)`. The same override idiom is described in [dependencies](pydantic-ai-dependencies.md)[^pydantic-workspace-docs]

Realtime sessions do not currently select workspaces even when the agent has a workspace capability; workspace tools in a realtime session report that limit instead of suggesting a second capability[^pydantic-workspace-docs]

## Limits

- The source is Pydantic's own workspace documentation with no version, author or date, and no run in it was executed here; every claim is **Reported**[^pydantic-workspace-docs]
- The precedence list, the `UserError` cases and the capability-ordering rule are stated in prose with no test or trace showing which branch ran; the two-capability migration sample depends on an `id=` parameter whose matching rules are only described as "recognizes it"[^pydantic-workspace-docs]
- Whether `workspace='new'` or an unrecognized reference fails before or after any model request is not stated, and no durable-engine capture confirms the run-start rebuild in this page — that ordering is on [durable tool placement](pydantic-ai-durable-tool-placement.md)[^pydantic-workspace-docs]
- No sandbox, message store or nested run was created, so the reference's round trip through `all_messages_json` and the client-side stripping by `sanitize_messages` were not observed[^pydantic-workspace-docs]

## Relationships

- **Selects among** the backends catalogued in [Pydantic AI workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md), and is where that page's cleanup rule actually bites.
- **Implements** the `get_workspace` extension point of the [capability primitive](pydantic-ai-capability-primitive.md), including its `defer_loading` incompatibility.
- **Carries** the provenance level described in [workspace file authority](pydantic-ai-workspace-authority.md) across the wrapper it accepts as `workspace=`.
- **Relies on** the reference contract in [workspace backends](pydantic-ai-workspace-backends.md): a backend's `ref` is what reattachment resolves, and a gone environment must raise rather than be recreated.
- **Interacts with** [Conversation state](pydantic-ai-conversation-state.md) and message-history persistence, since the reference travels inside the stored messages.
- **Is rebuilt per unit under** [durable execution](pydantic-ai-durable-execution.md), where a workflow re-derives the workspace from the agent's capabilities instead of carrying the `workspace=` object.
- **Is bounded by** [Pydantic AI run controls](pydantic-ai-run-controls.md) when a nested run shares `usage=ctx.usage`.
- **Has a known exclusion in** [realtime voice agents](pydantic-ai-realtime-voice.md), where a session does not select a workspace at all.

[^pydantic-workspace-docs]: Pydantic, "Workspaces" (pydantic.dev docs, `/docs/ai/core-concepts/workspace/`), 6,000 words as declared, 6,040 by local `wc -w`, no version, author or date stated; local capture `raw/core-concepts/workspace/index.md`, content digest sha256:106c823e. §"Give an agent an environment" (raw lines 12–50) and §"Move it into a sandbox" (51–65) for when a sandbox is created; §"Pick up where you left off" (66–109) for the precedence, the `WorkspaceRef` on `ModelResponse.workspace_ref`, the `all_messages_json()` round trip, the three reference rules and the `sanitize_messages` stripping; §"Hand the workspace to another agent" (110–142) for the reviewer sample; §"Choosing a run's workspace" (282–322) for the three-step precedence, the `workspace=` forms, capability ordering, the `LocalWorkspace` containment and symlink-spelling rule, and the failure table; §"Cleaning up" (323–328) for the failed-run `on_run_error` deletion; §"Supplying a workspace from a capability" (384–435) for `get_workspace`, the per-user example, `LocalWorkspaceBackend`, `ctx.workspace.attached`, the `override` idiom and the realtime limit. Evidence class: **Reported** — vendor reference documentation naming no version; nothing was constructed or run.
