---
type: Concept
title: Pydantic AI Harness E2B sandbox
description: The Harness E2BSandbox capability — a pause-not-kill sandbox that supplies the run's workspace and no tools, its Hobby-plan hour and Pro-plan day, login-shell command execution with a client-side deadline, the file-authority setting that wraps the workspace, the token-injecting network proxy that keeps a credential out of the sandbox, non-atomic E2B writes, and the preview-server, cleanup and spec boundaries around it.
tags: [pydantic-ai, agents, harness, sandboxing]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:40:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-e2b-sandbox-docs
    resource: ../raw/harness/e2b-sandbox/index.md
    scope: ../raw/harness/e2b-sandbox/
    kind: documentation
    revision: sha256:18ccb7ad3358aefb277f685880ee331e4f8fa646f9630816bbeaca4103fe3b53
    title: "E2B Sandbox"
---

`E2BSandbox` is the [Harness](pydantic-ai-harness.md) capability that makes an agent's commands and file edits run in an isolated [E2B](https://e2b.dev/) cloud sandbox[^pydantic-e2b-sandbox-docs] Like [Modal](pydantic-ai-harness-modal-sandbox.md) it **registers no tools** — it supplies the run's [workspace](pydantic-ai-workspaces-and-sandboxes.md) and pairs with `Coder`, `Shell`, `FileSystem` or your own `ctx.workspace` tools. What distinguishes it is its lifecycle: E2B **pauses** the sandbox at its timeout and the next run **resumes** it, where other backends let it die. The page names no Pydantic AI or Harness version, so every behaviour below is version-unknown.

This page supersedes nothing: the earlier vendor article on the same backend, compiled as [E2B sandbox recovery](pydantic-ai-e2b-sandbox-recovery.md), documents the same lifecycle and the Temporal recovery demonstration with different emphasis.

## Lifetime and resumption

| Fact | Value |
| --- | --- |
| Default `sandbox_timeout` | `3_600` seconds — one hour, the most E2B's **Hobby** plan allows |
| Pro plans | Up to `sandbox_timeout=86_400` (24 hours) |
| On expiry | The sandbox **pauses** rather than dies; the next run resumes it |
| Over your plan's limit | `WorkspaceUnavailableError`, with the limit in the message |
| Reattachment | `sandbox_timeout` applies on reattach as well as on create |
| `template`, `allow_internet_access`, `network` | Only shape a **new** sandbox |
| `working_dir`, `env` | Apply to **every** command, including after reattachment |

A follow-up run with `message_history=result.all_messages()` finds the sandbox in the history and works in it, so a clone survives; without history a run starts a new sandbox. A **killed** sandbox raises `WorkspaceUnavailableError` rather than silently starting over in an empty one, while a paused one resumes[^pydantic-e2b-sandbox-docs] `workspace=result.workspace.ref` reattaches without the history, `workspace='new'` forces a fresh sandbox, and the ref again holds no credentials — the reattaching process needs them too. `E2BSandboxBackend(sandbox=e2b.AsyncSandbox)` adopts a sandbox you created yourself, in which case `E2BSandbox`'s settings do not apply and `working_dir`/`env` go on the backend.

## The template and what it lacks

The default template is E2B's `base`: Python and git, **no ripgrep and no project dependencies**, not even `pytest`, and commands start in `/home/user` as the `user` account[^pydantic-e2b-sandbox-docs] Three consequences:

- `Coder` can search without `rg`, but installing it makes searches faster — build a reusable template once, outside a run, with `apt_install(['ripgrep'])`.
- Seed dependencies either in a custom template or through the workspace before the run (`Workspace(backend)` → `write_text` → `run(['pip', 'install', …])` → pass `backend` as `workspace=`), with the `finally` killing the sandbox even when setup or the run fails.
- Pass `working_dir='/home/user/project'` so the project is not the home directory that holds dotfiles and the pip cache; it is created on a new sandbox.

An unknown template raises `WorkspaceUnavailableError` on first use. `env` reaches every process in the sandbox and is readable by the agent's commands, so secrets the agent should not see must stay out; the default template's locale is POSIX, so `env={'LC_ALL': 'C.UTF-8'}` is what makes `wc -m` count characters rather than bytes.

## How a command runs

`E2BSandbox` supplies execution only; the backend satisfies both `SupportsCommands` and `SupportsFilesystem`, which is why `Shell` and `FileSystem` work on it unchanged[^pydantic-e2b-sandbox-docs] Commands are **one-shot**, with complete output returned after they finish, and every one of them runs through `/bin/bash -l -c`: an argv sequence is first quoted into a single shell word string, and the login startup files run before the command does; a `shell=True` string runs under `/bin/sh -c` *inside* that login shell.

The deadline is enforced **client-side** for a reason: E2B's own command `timeout` abandons the output stream and leaves the command running, so expiry has to stop the process group from Pydantic AI's side (see [what a timeout stops](#what-a-timeout-stops-and-what-it-does-not)), and it applies while the command is still starting as well as while it runs. Two consequences follow (**Synthesis**, from those mechanics rather than stated in the source): an argv element stays one argument only if the quoting survives the join into a single shell word string, so passing argv is safer than a string but not by itself a guarantee against shell parsing; and every command re-runs the login profile, so a custom template whose profile prints or fails affects every command the agent issues.

`working_dir` and `env` are applied per command in this path[^pydantic-e2b-sandbox-docs]: E2B has no create-time working directory, so `working_dir` is set on every command, including on an attached sandbox; with `None` the backend discovers the sandbox's own default with `pwd -P` on first use, and the async `working_dir()` returns that canonical absolute path. `env` reaches every command on a created or an attached sandbox, a per-command `env` is layered on top of it, and nothing is read from the host environment.

## File authority

`authority` defaults to `'operator'` — files this side wrote — and the two levels worth reaching for are `'none'` for a sandbox holding what nobody on your side wrote, such as a cloned third-party repository, and `'user'` for the user's own files[^pydantic-e2b-sandbox-docs] Anything **below** `'operator'` wraps the backend in an `AuthorityWorkspace`, and `get_workspace` hands back the workspace in that wrapper when `authority` or `path_authority` asks for one, so a capability that lifts a sandbox file into the prompt cannot give it more standing than the file carries. `path_authority` overrides the level per directory or file with the longest matching path winning, and its keys are **sandbox** paths — a relative one resolves against the working directory, and `~` is not expanded. What the levels do to prompt provenance, and how symlinks and case are resolved, is in [workspace file authority](pydantic-ai-workspace-authority.md).

## The agent-spec boundary

`E2BSandbox.from_spec()` names ten spec-expressible fields — `id`, `description`, `defer_loading`, `template`, `allow_internet_access`, `sandbox_timeout`, `working_dir`, `env`, `authority` and `path_authority` — so a spec can shape a sandbox but cannot credential it: `client` cannot be set from a spec, and neither can `network`[^pydantic-e2b-sandbox-docs] Core reads that signature to generate the spec's JSON schema. A subclass that inherits `from_spec` instead falls back to the variadic base signature, because `client`'s `e2b.E2B` hint is a `TYPE_CHECKING` import, and its spec then publishes only the bare `'E2BSandbox'` name.

## Credentials: the network proxy

`E2BSandbox(client=E2B(api_key=…))` sets one client for the capability in place of `E2B_API_KEY`, and the environment holds one key for the whole process — so per-user accounts need a capability of your own whose `get_workspace` builds `E2BSandboxBackend(client=…, ref=ref)` from the run's `deps`[^pydantic-e2b-sandbox-docs] Two traps are specific to E2B:

- **The client falls back to `E2B_API_KEY` when its key is empty or `None`.** If that variable is set where the app runs, a user with no key would silently run on *that* account, so check for a key before building the client.
- Under Temporal, `deps` are serialized into the workflow history, so an API key on them is a credential in durable storage: put a user id there and look the key up on the worker.

The capability offers a stronger answer for the *sandbox's* credentials: `network` passes E2B's own network options to `Sandbox.create`, and E2B can add an `Authorization` header as each request **leaves** the sandbox, so a GitHub token is never inside it — `gh` and `git push` work as the token's owner while `echo $GH_TOKEN` prints `placeholder`[^pydantic-e2b-sandbox-docs] The caveats are part of the design rather than fine print:

- Only **HTTPS** requests get the header, so remotes must be `https://`, not `git@github.com:…`.
- If you also set `allow_out` or `allow_internet_access=False`, each host in `rules` must appear in `allow_out` or its requests are blocked.
- The agent cannot see the token but **can use it** for anything the token allows.
- List only hosts that never echo request headers back in a response, or a command could read the token there.
- An attached sandbox keeps its rules; changing them — swapping the token, say — means `update_network` on `await backend.get_sandbox()`, which replaces **all** network options at once.
- To keep the token out of the create request too, save the header value as an E2B secret and use `e2b.Secret.fill(name)`.

E2B calls this feature **public beta**, so it may change. `network` also cannot be set from a spec.

## What a timeout stops, and what it does not

On timeout or cancellation the backend sends **TERM then KILL to the command's process group**, children included unless they moved to another process group or session, and the sandbox keeps running[^pydantic-e2b-sandbox-docs] Four boundary conditions:

- Custom templates need `/bin/bash` and `/bin/sh`; without `setsid` (util-linux) only the command's own process is stopped.
- Stopping is **best effort**: if E2B cannot be reached the command may keep running, so keeping the ref is how you inspect or kill the sandbox.
- A command whose combined output passes **10 MiB** is stopped the same way and raises `WorkspaceOutputLimitError`, with the first 65,536 characters of each stream in `stdout`/`stderr` — redirect large output to a file instead.
- A command killed by a signal may return **`exit_code=-1`**; the SDK does not identify the signal, so this is *not* converted to `128+signal` — any code that inspects exit codes must treat `-1` as a signal death rather than an ordinary failure.

Three more platform facts that change what tools can assume[^pydantic-e2b-sandbox-docs]: E2B's file service reads and writes with its own root privileges, so **Unix permissions do not restrict file operations** — do not rely on them to keep file tools out of a path; **concurrent writes to the same path are not atomic**, so uploads may interleave and a reader can see a partial file, which means coordinating writers or writing to separate paths; reading a FIFO raises `OSError` instead of waiting for a writer; and E2B's file API leaves looping symlinks out of directory listings. A background child that inherits stdout or stderr can also keep `run()` waiting for the SDK stream to close after the main command exits, so a long-running job should redirect its output to a file (`Shell.start_command` manages its own log).

## Previewing a dev server

The source documents a full preview workflow, which is the only place in the capture where E2B's own API is used alongside the workspace[^pydantic-e2b-sandbox-docs]: with `Shell`, ask the agent to `start_command` `npm run dev -- --host 0.0.0.0 --port 3000`, poll `check_command` and `curl http://localhost:3000/health` until ready, and save the returned command ID. Given the workspace ref, `await capability.backend(ref).get_sandbox()` returns the sandbox — using the *capability's* backend so its `sandbox_timeout` applies — and `sandbox.get_host(3000)` gives the public hostname to prefix with `https://`. When done, `stop_command` with the ID **while the workspace is attached**, then `await E2BSandbox().destroy(ref)`. A public preview should not outlive its use.

## Cleanup

Pydantic AI does not kill the sandbox[^pydantic-e2b-sandbox-docs] A sandbox you do not kill is **paused** when its `sandbox_timeout` runs out; `destroy(ref)` kills by ID with the instance's `client`, without attaching, and kills a paused sandbox without resuming it.

The typed handle has its own contract[^pydantic-e2b-sandbox-docs]: building `E2BSandboxBackend` does no I/O and the first operation creates or attaches, while `get_sandbox()` on a backend with no sandbox **creates one, which E2B bills**, or attaches to the one `ref` names and resumes it if paused. A `ref` naming a sandbox that no longer exists raises `WorkspaceUnavailableError` and **no replacement is created**; afterwards the cached handle is returned **without re-checking that the sandbox is still running**, so one killed elsewhere surfaces on the next operation. Calling it does not make you responsible for killing the sandbox — whoever holds the ref decides, and a backend built with `sandbox=e2b.AsyncSandbox` leaves killing to whoever created that sandbox.

The failure paths are slightly better than Modal's and worth stating separately: if a run is cancelled while E2B creates the sandbox, the ref **is** still recorded once E2B answers, and the id is logged either way; if E2B's answer never arrives, the sandbox can exist with **no ref and no log entry**, so it has to be found and killed in the E2B dashboard. A failed run returns no result and `after_run` does not run, so termination belongs in an `on_run_error` hook — shielded with `anyio.move_on_after(30, shield=True)` and then re-raising.

## Durable execution, telemetry and the event loop

Temporal composition is the same as any workspace: `E2BSandbox()` + `Coder()` + `TemporalDurability()`, agent and workflow at module level, and `Coder(repo_context=False)` for lazy creation[^pydantic-e2b-sandbox-docs] Removing a capability while workflows use it changes their replay history — drain or version before deploying.

`E2BSandbox` emits no spans of its own; core instrumentation records `pydantic_ai.workspace.provider` and `pydantic_ai.workspace.id` on the agent run span, tool operations inside the tool-call span, run-start operations such as `RepoContext` loading in the run span, and creation as `Created E2B sandbox <id>` at INFO on `pydantic_ai_harness.e2b_sandbox._backend`[^pydantic-e2b-sandbox-docs]

The E2B SDK runs every request on asyncio, so under **Trio** every operation — `destroy` included — raises `UserError` before it reaches E2B.

## Coverage and limits

The package is the single `index.md` capture with no attachments, includes or supporting files; the flow diagram and every code sample were read in their text forms[^pydantic-e2b-sandbox-docs] External links — E2B's template quickstart, internet-access documentation and sandbox lifecycle, plus Temporal worker versioning, the workspaces and instrumentation pages and the Pydantic E2B article — were read as links and not followed. The page names no version, date, author or licence, so the concept is `draft` under the `pydantic-ai` domain rule; its examples pin `anthropic:claude-opus-5-5`, an alias no release pin corroborates.

Nothing was installed, no sandbox created, paused, resumed, previewed or killed, no command run and no trace opened, so every claim is **Reported** and none **Observed** or **Reproduced**. The source does not state how long a paused sandbox is retained, what pause and resume cost, whether `get_host` exposes only the requested port or the whole machine, or what the 10 MiB output cap does to the agent's retry budget. It also describes the command path as a `sh -c` login-shell environment in one place and as `/bin/bash -l -c` in another without reconciling the two, and never names the serializer that joins an argv sequence into one shell word string.

## Relationships

- **Alternative to** [Harness Modal sandbox](pydantic-ai-harness-modal-sandbox.md) and the other workspace backends; the composed code is identical.
- **Same subject as** [E2B sandbox recovery](pydantic-ai-e2b-sandbox-recovery.md), which documents the lifecycle through a measured pause/resume and Temporal worker-kill demonstration rather than an API page.
- **Provides a** [workspace](pydantic-ai-workspaces-and-sandboxes.md) for [Coder](pydantic-ai-harness-coder.md), [Shell](pydantic-ai-harness-shell.md) and [FileSystem](pydantic-ai-harness-filesystem.md), and no tools of its own.
- **Composes with** [durable execution](pydantic-ai-durable-execution.md) through the credential-free ref, and with [workspace file authority](pydantic-ai-workspace-authority.md) through `authority`/`path_authority`.
- **Runs under** [Pydantic AI observability](pydantic-ai-observability.md), where the workspace id is the correlation key between runs.
- **Is bounded by** the [agent-spec surface](pydantic-ai-agent-specs.md), which can shape the sandbox but not credential it: `client` and `network` stay in Python.

[^pydantic-e2b-sandbox-docs]: Pydantic Docs, "E2B Sandbox", <https://pydantic.dev/docs/ai/harness/e2b-sandbox/>; local capture `raw/harness/e2b-sandbox/index.md`, content digest sha256:18ccb7ad, 4,125 words as declared (4,194 by `wc -w`), 644 lines, no publication date, author, licence or Pydantic AI/Harness version. Locators are line ranges in that capture: 11 for the one-line purpose; 13–41 for the flow diagram (tools → `get_workspace` → E2B sandbox, paused at timeout, killed by `destroy`, ref-based reattach and resume); 43–63 for the install extras and quick start; 65–85 for the hour/day lifetime, the pause-and-resume rule, `/home/user`, the missing `rg` and the template build; 87–99 for continuing in the same sandbox from history; 101–124 for tool choice, the `user` account, the root-privileged file service, FIFO and symlink behaviour, the background-stream hang and the timeout/`exit_code=-1`/10 MiB rules; 126–140 for reattachment and which settings apply where; 142–170 for per-user clients, the `E2B_API_KEY` fallback trap and the destroy-account trap; 172–204 for seeding a sandbox before the run; 206–230 for the token-injecting network proxy and its caveats; 232–238 for the dev-server preview; 240–280 for cleanup, the cancelled-creation ref, the `on_run_error` hook and pause-on-timeout; 282–304 for the nine configuration options; 306–312 for asyncio-only; 314–350 for the Temporal example and replay-history warning; 352–358 for telemetry; 360–643 for the API reference, of which 383–391 records that the capability supplies execution only, 439–449 the authority levels and the `AuthorityWorkspace` wrap, 461–484 the ten `from_spec` fields with the `TYPE_CHECKING` fallback, 516–526 `get_workspace`'s wrapper rule, 534–544 the one-shot `/bin/bash -l -c` command path with the client-side deadline (`shell=True` under `/bin/sh -c`, timeout while starting included), 576 and 580 `working_dir`'s `pwd -P` discovery and the per-command `env` layering, and 596–606 the `get_sandbox()` contract. Evidence class: **Reported** — vendor documentation for its own package, with no execution behind it.
