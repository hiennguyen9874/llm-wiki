---
type: Concept
title: Pydantic AI Harness Modal sandbox
description: The Harness ModalSandbox capability — a sandbox that supplies the run's workspace and registers no tools, its 24-hour default lifetime and explicit cleanup, ref-based reattachment and the credential-free ref, per-user Modal clients, the fields a spec can and cannot express, and the timeout, output, network and replay boundaries it does not remove.
tags: [pydantic-ai, agents, harness, sandboxing]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:34:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-modal-sandbox-docs
    resource: ../raw/harness/modal-sandbox/index.md
    scope: ../raw/harness/modal-sandbox/
    kind: documentation
    revision: sha256:46604b73962e8017afa8752d462e4a7c5d1ac41e19e4b92745dc2942ced5ed45
    title: "Modal Sandbox"
---

`ModalSandbox` is the [Harness](pydantic-ai-harness.md) capability that makes an agent's commands and file edits run in an isolated [Modal](https://modal.com/) cloud sandbox instead of on your machine[^pydantic-modal-sandbox-docs] Its shape is the important part: it **registers no tools**. It supplies the run's [workspace](pydantic-ai-workspaces-and-sandboxes.md), and `Coder`, `Shell`, `FileSystem` or your own `ctx.workspace` tools do the work inside it — the current architecture in which a sandbox is a workspace backend rather than a tool bundle. It is the same slot as [E2B](pydantic-ai-harness-e2b-sandbox.md), and the choice between them is a provider decision, not an API one. The page names no Pydantic AI or Harness version, so every behaviour below is version-unknown.

```python
agent = Agent('anthropic:claude-opus-5-5', capabilities=[ModalSandbox(), Coder()])
```

`Coder`'s shell and file tools now run in the sandbox, and `Coder`'s `RepoContext` creates it when the run starts — `Coder(repo_context=False)` defers creation to the first tool call[^pydantic-modal-sandbox-docs] If only your own tools use the sandbox, `warn_if_no_tools=False` silences the missing-`Shell`/`FileSystem` warning, or filter `ModalSandboxNoToolsWarning`.

## The lifecycle is the contract

This is where a sandbox backend differs most from a library call, and the source is explicit[^pydantic-modal-sandbox-docs]:

- A new sandbox lives for up to **24 hours** — Modal's maximum — by default (`sandbox_timeout=86_400`, where Modal accepts 10–86,400), and `sandbox_timeout=3600` shortens it; `idle_timeout` ends it after that many seconds without activity.
- **Pydantic AI never terminates it.** The sandbox keeps running, and **billing**, after the run ends; termination is the application's job through `await ModalSandbox().destroy(ref)` with a ref you stored.
- `destroy(ref)` uses the sandbox ID directly with the instance's `client`: it does not resume an expired sandbox or run its tools, a sandbox that no longer exists returns quietly, and a sandbox whose image command ignores Modal's stop signal can keep running for roughly 30 seconds after `destroy` returns. Only destroy sandboxes you own.
- A **failed run returns no result**, so there is no ref to store and `after_run` does not run; cleanup belongs in an `on_run_error` hook — shielded with `anyio.move_on_after(30, shield=True)` so an outer deadline cannot cut the kill short and a hung API call cannot hang the run.
- A run cancelled while Modal is still **creating** the sandbox leaves no ref for any hook; the ID is logged at `WARNING` on `pydantic_ai_harness.modal_sandbox._backend`, so terminate it with `ModalSandbox().destroy(WorkspaceRef(provider='modal', id=…))`. Creation succeeds logs the same ID at `INFO`.

`ModalSandbox().backend(ref)` builds a backend for an existing ref without I/O, and `ModalSandboxBackend(sandbox=modal.Sandbox)` adopts a sandbox you created yourself — the route for Modal features the workspace API does not cover, such as `block_network`[^pydantic-modal-sandbox-docs] A backend's `get_sandbox()` returns the typed `modal.Sandbox`: on a backend with no sandbox yet it **creates one, which Modal bills**, or attaches to the one `ref` names, raising `WorkspaceUnavailableError` when that sandbox no longer exists instead of making a replacement. After that it hands back the **cached handle without re-checking liveness**, so a sandbox killed elsewhere surfaces on the next operation, and calling it does not move the termination duty — whoever holds the ref still decides.

## Reattachment and the ref

A workspace outlives its run, and two routes reconnect[^pydantic-modal-sandbox-docs]:

| Route | Effect |
| --- | --- |
| `message_history=result.all_messages()` | The follow-up run finds the sandbox **in the history** and works in it, so a clone is still there |
| `workspace=result.workspace.ref` | Reattaches without the history; the ref holds **no credentials**, so the reattaching process needs your Modal credentials too |
| `workspace='new'` | Forces a fresh sandbox even when the history names one |

Reattaching to a **terminated or expired** sandbox raises `WorkspaceUnavailableError` rather than silently starting over in an empty one — the same failure surfaces when a command exits 137 because the sandbox was terminated mid-command, while a SIGKILLed command inside a running sandbox returns 137 as an ordinary exit[^pydantic-modal-sandbox-docs]

Only some settings shape a **new** sandbox: `image`, `app_name`, `create_app_if_missing`, `sandbox_timeout`, `idle_timeout`. `working_dir` and `env` apply to every command, including after reattachment. That asymmetry is the practical one to remember.

## The default image and what is missing from it

The default image is Debian slim running as **root in `/root`** with Python 3.12, `git` and `ripgrep` — and **none of your project's dependencies**, not even `pytest`[^pydantic-modal-sandbox-docs] Two ways to fix that: a custom `image` (a registry tag or a `modal.Image`), or seeding through the workspace before the run — create the backend, write files and `pip install` through `Workspace`, then pass the backend as `workspace=`. A first use may take several minutes while Modal builds or pulls an image, and a sandbox that cannot start (a missing image, say) raises an error saying why. `working_dir='/root/project'` keeps the project out of the home directory and is created on a new sandbox; on an attached or caller-supplied sandbox it must already exist.

`env` is the only environment that reaches the sandbox: **nothing from your machine's environment** does, and every `env` value is readable by the model and by anything it runs, including a cloned repository's code[^pydantic-modal-sandbox-docs]

## Timeouts and output limits

`run(timeout=...)` starts its clock **after** sandbox acquisition and covers command start, execution and output collection[^pydantic-modal-sandbox-docs] On its deadline or on cancellation the backend attempts to stop the command's **foreground process group** — not the shared sandbox and not detached background jobs — and partial stdout and stderr are available on `WorkspaceTimeoutError`. Two caveats:

- if the stop RPC fails, the command may still be running, so keeping the ref for explicit cleanup matters;
- on a custom or attached image without util-linux's `setsid`, a deadline stops only the wrapper process, not its children — installing util-linux is what makes cancellation reach them.

`timeout=None` removes the command deadline but not the sandbox's own lifetime or idle settings. `run()` takes the command as a list or, with `shell=True`, as a string executed as `/bin/sh -c <command>`. `Shell` sets 30 seconds by default; a hand-written tool passes its own. A command whose combined stdout and stderr pass **10 MiB** is stopped and raises `WorkspaceOutputLimitError`, which is the sandbox's own bound rather than `max_output_chars`. Sandbox creation that does not finish within **10 minutes** raises `TimeoutError` and is *not* covered by `WorkspaceError`; transient Modal errors propagate unchanged so a durable engine can retry them.

## Per-user credentials

`ModalSandbox(client=modal.Client.from_credentials(...))` sets one client for the capability, in place of the environment and config file — and Modal keeps **one** client from the environment for the whole process, so that cannot serve several users at once[^pydantic-modal-sandbox-docs] When each user has their own Modal account, the solve is a capability of your own whose `get_workspace(ctx, *, ref)` builds `ModalSandboxBackend(ref=ref, client=ctx.deps.modal_client)`; building a Modal client opens a connection, so it must be built ahead of the run because `get_workspace` must not do I/O. Under [Temporal](pydantic-ai-durable-execution.md) `deps` are serialized for every activity, so the client cannot live there: put a user id in `deps` and look the client up on the worker.

Another cross-account trap: destroying a user's sandbox with **another account's** client may not find it, and a sandbox that is not found returns quietly — so it would keep running and billing with no error[^pydantic-modal-sandbox-docs]

## Agent specs and the no-tools warning

`ModalSandbox.from_spec()` names the fields a spec can express — `id`, `description`, `image`, `app_name`, `create_app_if_missing`, `sandbox_timeout`, `idle_timeout`, `working_dir`, `env`, `warn_if_no_tools`, `authority` and `path_authority`[^pydantic-modal-sandbox-docs] Core reads that signature to build the spec's JSON schema, but a subclass that inherits `from_spec` falls back to the variadic base, because `__init__`'s `modal.Image` hint is a `TYPE_CHECKING` import, so its schema publishes only the bare `'ModalSandbox'` and a spec names an image by its **registry tag**. Two fields stay out of reach: `client` **cannot be set from a spec**, so per-user credentials remain a Python-side custom capability, and `**kwargs` reaches `__init__` unchanged, so `defer_loading` keeps its refusal instead of being accepted silently.

The `warn_if_no_tools` warning is a development aid with two rough edges: it checks **tool names only**, so a custom tool that reaches the sandbox under another name still does not count, and the flag and its warning are slated to go away in the stable Harness release.

## Isolation is from your machine, not from the network

The sandbox has **outbound internet access** by default, and files nobody on your side wrote — a cloned third-party repository — should be treated accordingly[^pydantic-modal-sandbox-docs] The capability models that with `authority` (`'operator'` by default, `'none'` for untrusted files, `'user'` for the user's own) and `path_authority` for per-path overrides where the longest matching path wins, reported through `authority_of` so a capability can send a file's text with no more authority than the file has — see [workspace file authority](pydantic-ai-workspace-authority.md). Network restrictions such as Modal's `block_network` require creating the `modal.Sandbox` yourself and passing `ModalSandboxBackend(sandbox=…)`.

One runtime constraint: Modal runs on the asyncio event loop only, so under **Trio** the backend raises `UserError`.

## Durable execution and telemetry

`ModalSandbox` composes with Temporal the same way any workspace does — `TemporalDurability()` beside it, agent and workflow defined at module level for activity registration, and `Coder(repo_context=False)` if the sandbox should be created lazily[^pydantic-modal-sandbox-docs] The one deployment warning: removing a capability while workflows that use it are still running changes their replay history, so drain those workflows or use Temporal worker versioning before deploying.

`ModalSandbox` emits **no spans of its own**[^pydantic-modal-sandbox-docs] Core instrumentation records `pydantic_ai.workspace.provider` and `pydantic_ai.workspace.id` on the agent run span, each command or file operation runs inside its tool call's span, and run-start operations such as `RepoContext` loading instructions land in the agent run span. Sandbox IDs are the correlation key between the two — the same pattern the [E2B](pydantic-ai-e2b-sandbox-recovery.md) write-up measures.

## Migrating from the previous ModalSandbox

The upgrade section is a migration table, and one row changes behaviour rather than names[^pydantic-modal-sandbox-docs]: the previous `ModalSandbox` registered its own `run_command`, `read_file`, `write_file` and `list_directory` tools and **terminated its sandbox when the run ended**. Now it only supplies the sandbox, so `Coder()` or `Shell()` + `FileSystem()` must be added; old arguments still construct with a `HarnessDeprecationWarning` naming the replacement and are ignored.

Consequences worth carrying[^pydantic-modal-sandbox-docs]:

- `sandbox_timeout` defaults to 24 hours instead of 300 seconds, and a run no longer terminates the sandbox.
- `workdir` became `working_dir`; the default working directory is `/root` on the default image where the old `python:3.12-slim` image started in `/`, and a custom image keeps its own `WORKDIR`.
- `sandbox_id` is deprecated in favour of `WorkspaceRef(provider='modal', id=…)`; `session`/`ModalSandboxSession` gave way to `workspace=ModalSandboxBackend(sandbox=…)`.
- `default_command_timeout` became `Shell(default_timeout=…)`, and `max_command_timeout` has **no equivalent** — nothing caps a timeout the model asks for.
- `max_output_bytes`/`max_output_lines` became `Shell(max_output_chars=…)` or `ToolOutputLimits`, with the 10 MiB combined-output stop as the hard ceiling; `max_read_bytes` became `FileSystem(max_read_lines=…, max_read_chars=…)`.
- `FileSystem` reaches only the working directory where the old tools reached the whole sandbox — use `FileSystem(root_dir='/')` — and `read_file`'s `offset` is now zero-based where the old tool counted from 1.
- `PrefixTools(ModalSandbox(...), prefix='modal')` next to `Shell()`/`FileSystem()` is obsolete: the `modal_*` tools are gone and the unprefixed tools now run in the sandbox.
- The `ModalSandbox*Error` classes collapsed into `pydantic_ai.workspaces.WorkspaceError` and `WorkspaceUnavailableError`; `ModalSandboxExecResult` became `workspaces.CommandResult`.

## Coverage and limits

The package is the single `index.md` capture with no attachments, includes or supporting files; the flow diagram and every code sample were read in their text forms[^pydantic-modal-sandbox-docs] External links — Modal's timeouts documentation, Temporal worker versioning, the workspaces and instrumentation pages, and the Pydantic article "The agent outgrew your laptop" — were read as links and not followed. The page names no version, date, author or licence, so the concept is `draft` under the `pydantic-ai` domain rule; its examples pin `anthropic:claude-opus-5-5`, an alias no release pin corroborates.

Nothing was installed, no sandbox created, attached, timed out or destroyed, no command run and no trace opened, so every claim is **Reported** and none **Observed** or **Reproduced**. The source does not state Modal's per-second sandbox price, how long image builds are cached, what `WorkspaceOutputLimitError` does to the agent's retry budget, or whether `idle_timeout` counts a foreground command's runtime as activity — the four unknowns that decide what an unattended deployment costs.

## Relationships

- **Provides a** [workspace](pydantic-ai-workspaces-and-sandboxes.md) and registers no tools; pair it with [Coder](pydantic-ai-harness-coder.md), [Shell](pydantic-ai-harness-shell.md) and [FileSystem](pydantic-ai-harness-filesystem.md).
- **Alternative to** [Harness E2B sandbox](pydantic-ai-harness-e2b-sandbox.md) and the other sandbox backends; the same code runs on either.
- **Composes with** [durable execution](pydantic-ai-durable-execution.md): the ref is the checkpointable identity, and a replay reattaches rather than recreating.
- **Interacts with** [workspace file authority](pydantic-ai-workspace-authority.md) through `authority` and `path_authority`, and with [observability](pydantic-ai-observability.md) through the `pydantic_ai.workspace.*` span attributes.

[^pydantic-modal-sandbox-docs]: Pydantic Docs, "Modal Sandbox", <https://pydantic.dev/docs/ai/harness/modal-sandbox/>; local capture `raw/harness/modal-sandbox/index.md`, content digest sha256:46604b73, 4,231 words as declared (4,315 by `wc -w`), 654 lines, no publication date, author, licence or Pydantic AI/Harness version. Locators are line ranges in that capture: 11 for the one-line purpose; 13–41 for the flow diagram (tools on your machine, `get_workspace` hook, the sandbox, the ref in history, `WorkspaceUnavailableError`); 43–63 for install credentials and the quick start, including `RepoContext` creating the sandbox at run start; 65–73 for the 24-hour default, the default image and `working_dir`; 75–89 for continuing in the same sandbox from history; 91–112 for choosing tools, the custom `run_python` tool, `warn_if_no_tools` and the FIFO/device `OSError`; 114–124 for what a timeout stops and the `setsid` caveat; 126–146 for ref-based reattachment, `workspace='new'` and which settings apply to new sandboxes; 148–178 for per-user clients, the `get_workspace` note and the `destroy` account trap; 180–205 for preparing a sandbox before the run and the cancelled-creation warning log; 207–245 for cleanup, `destroy`, the failed-run `on_run_error` hook and the 30-second stop lag; 247–270 for the 13 configuration options, including the `sandbox_timeout` 10–86,400 range at 255 and the `warn_if_no_tools` default at 260; 272–274 for asyncio-only and the network/`env` isolation caveat; 276–312 for the Temporal example and the replay-history warning; 314–320 for telemetry; 322–352 for the upgrade notes and the migration table; 354–653 for the API reference, of which 424 is `client` being unsettable from a spec, 428–440 is what the no-tools warning actually checks and when it is removed, 459–481 is `from_spec`'s spec-expressible fields with the registry-tag-only image and the `TYPE_CHECKING` schema fallback, 596–602 is `get_sandbox`'s create-or-attach, cached-handle and termination-ownership rules, and 642 is `/bin/sh -c`. Evidence class: **Reported** — vendor documentation for its own package, with no execution behind it.
