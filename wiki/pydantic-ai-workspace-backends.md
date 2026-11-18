---
type: Concept
title: Pydantic AI workspace backends
description: The WorkspaceBackend contract behind ctx.workspace — the command and filesystem capability protocols, the ref lifecycle a backend owns, symlink resolution, the conformance suite that checks it, and the escape hatch that bypasses policies.
tags: [pydantic-ai, workspaces, sandboxing, backend]
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

The workspace a tool sees through `ctx.workspace` is a wrapper, not the environment itself. A `WorkspaceBackend` talks to one environment — a directory, a container, a sandbox API — and `Workspace` wraps it to give tools the uniform `ctx.workspace` methods, so writing a new provider means implementing the backend contract rather than another set of tools[^pydantic-workspace-docs]

## Backend versus workspace

A backend implements `ref` and `working_dir`, then adds `SupportsCommands`, `SupportsFilesystem`, or both. The source's own sandbox sample implements `ref`, `working_dir` and a `run` method over a placeholder provider SDK[^pydantic-workspace-docs]

| Backend implements | What `ctx.workspace` gives |
| --- | --- |
| `SupportsCommands` only | File operations are derived through the shell; shell-derived reads require regular files, not FIFOs or devices, and transfer large files and listings in bounded chunks, so they are slower than native provider file APIs |
| `SupportsFilesystem` only | File tools work and `run` raises `UserError` — a filesystem-only backend also works without shell support on a non-POSIX host |
| Both | They must reach the same environment |

Local and shell-derived file operations refuse to remove the workspace root or an ancestor, and local writes do not recreate a removed workspace directory[^pydantic-workspace-docs]

## The ref lifecycle a backend owns

`Workspace` holds no lock, so the backend owns get-or-create, and the documented rules are all consequences of that[^pydantic-workspace-docs]:

- The constructor does no I/O. The first operation creates the environment, or attaches to the one `ref` names.
- `ref` is `None` until the environment exists, then names it and never changes. Set it as soon as the create call returns, before any setup that can fail, so a failed setup still leaves a reference to clean up. Durable execution needs it set once any operation has completed.
- Concurrent first operations must create only one environment and share its reference, which the sample does with an `anyio.Lock`.
- A caller cancelled while the environment is being created must not lose its reference: recording it has to finish even though the caller has gone. The sample skips this, and the source points at the Harness sandboxes for a worked approach.
- A `ref` whose environment is gone raises `WorkspaceUnavailableError`. The backend never creates a replacement for it, never destroys the environment when a run ends, and never stops a process a command detached into its own session — the Harness `Shell` background jobs depend on the last rule.
- A non-zero exit is a result, not an exception. A program that cannot start is exit 127 (not found) or 126 (not executable), as in `sh`; a path-level failure raises the builtin file error; a timeout raises `WorkspaceTimeoutError`; a provider SDK's transient error is left to propagate so a durable engine can retry it.

## Resolving symlinks

`Workspace.realpath` answers "which file does this path really lead to?", and code that keeps an agent inside a directory needs that answer because a symlink can make a path that looks inside lead outside. File methods open `resolve(path)`, which collapses `..` as text, so a policy check must use `realpath(await ws.resolve(path))`; `realpath(path)` on the raw path follows the kernel, where `..` climbs from a symlink's target — with a check allowing only `/app` and a link `/app/data -> /secrets`, `/app/data/key` looks inside but opens `/secrets/key`[^pydantic-workspace-docs]

Backends answer in one of three ways[^pydantic-workspace-docs]:

- `LocalWorkspaceBackend` uses `os.path.realpath`.
- A backend with commands but without `SupportsRealpath` gets a shell fallback that follows links with `readlink` in one command; a link it cannot read, as in an image without `readlink`, raises `WorkspaceError` rather than staying unresolved.
- A backend with neither only gets the path normalized as text. That is exact for storage that cannot hold symlinks, such as an object store; where symlinks can exist, a path check such as the Harness `FileSystem`'s `root_dir` sees only the text and the check can be defeated.

The check and the later file operation are separate calls, so a link swapped in between is not caught. This is a preflight, not a security boundary: for untrusted code the source says rely on the sandbox, not on path checks[^pydantic-workspace-docs]

## Checking a backend

`WorkspaceBackendSuite` turns the backend contract into tests: subclass it in a pytest suite and provide its `backend` fixture, and each rule is one test. It needs the anyio pytest plugin, which runs every rule on each installed async backend — override the `anyio_backend` fixture to `'asyncio'` for an asyncio-only SDK[^pydantic-workspace-docs]

- A class-scoped `backend` fixture starts one environment for the whole suite instead of one per rule.
- Under durable execution every workspace call rebuilds the backend from its reference, so `attach_backend` — a factory that builds a backend for a reference the way the capability's `get_workspace` does — enables the rules that an attached backend reaches the same files and commands, keeps that reference, and finds a process an earlier command detached still running.
- `destroy_environment` and `destructive_backend` (an independent environment, defaulting to `fresh_backend` when supplied) enable the destruction rules; the destructive rule never uses the shared `backend` fixture.
- Four boolean fixtures, all `True` by default, declare a known limit and belong at `False` only for a limit documented for users: `can_detect_exit_with_inherited_output_pipes`, `filesystem_honors_shell_permissions`, and `has_real_posix_shell` plus `enforces_parent_file_errors` for in-memory test doubles.
- A skipped rule is not a passed rule: run pytest with `-rs` to see what went unchecked.

The suite's class, fixtures, switches and rule names are stable in 2.x, so renaming one is a breaking change, while new or stricter rules may arrive in a minor release — the documented remedy is to pin `pydantic-ai` if a new rule failing CI is a problem[^pydantic-workspace-docs]

## Third-party backends and the escape hatch

`pydantic-ai-backend`, a community package by Vstorm, implements the same interface over Kubernetes pods, local Docker containers, Daytona, a `sandboxd` service that holds the Docker socket so the application container need not, and in-memory JSON documents an application can keep in its own database[^pydantic-workspace-docs]

A capability's `get_workspace` returns the backend, and `ctx.workspace.backend` reaches its provider-specific methods. That is a provider API escape hatch and it bypasses wrapper policies such as `read_only`, so the `ctx.workspace` file and command methods are the policy-respecting route[^pydantic-workspace-docs]

## Limits

- The source is Pydantic's own workspace documentation, names no Pydantic AI release version, and carries no measurement; every claim is **Reported**[^pydantic-workspace-docs]
- The sample backend is illustrative and incomplete by the source's own admission — it omits the cancellation rule and leans on the Harness sandboxes for the settled version, which were read as a link and not inspected[^pydantic-workspace-docs]
- Which concrete methods `SupportsCommands`, `SupportsFilesystem` and `SupportsRealpath` require is deferred to API reference links that were read as links, not followed, so this page names the protocols and their consequences rather than their signatures[^pydantic-workspace-docs]
- The conformance suite was not run and no backend was written here; the rule list and the claim that a `'windows'` backend's commands are checked in PowerShell come from the documentation alone[^pydantic-workspace-docs]
- `pydantic-ai-backend` is named once, with no version, licence or test status, so its conformance to this contract is unverified[^pydantic-workspace-docs]

## Relationships

- **Underlies** [Pydantic AI workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md): that page records the `ctx.workspace` surface and the sandbox catalogue; this one records what a provider must implement behind it.
- **Is selected through** [workspace selection](pydantic-ai-workspace-selection.md): `get_workspace` returns a backend, and the `ref` rules here are what reattachment depends on.
- **Must not silently widen** [workspace file authority](pydantic-ai-workspace-authority.md): a backend's `authority_of` supplies the level a capability puts in the prompt.
- **Is exercised by** the [Harness](pydantic-ai-harness.md) sandbox capabilities, whose `attach_backend`-style behaviour the conformance suite's optional rules check.
- **Rebuilds per unit under** [durable execution](pydantic-ai-durable-execution.md), where every workspace call attaches a fresh backend from the reference.

[^pydantic-workspace-docs]: Pydantic, "Workspaces" (pydantic.dev docs, `/docs/ai/core-concepts/workspace/`), 6,000 words as declared, 6,040 by local `wc -w`, no version, author or date stated; local capture `raw/core-concepts/workspace/index.md`, content digest sha256:106c823e. §"Writing a backend" (raw lines 442–459) for the backend/`Workspace` split, the two `Supports*` protocols and their consequences, the root-removal refusal and the symlink-spelled reference; §"Resolving symlinks" (446–459) for the three resolution answers, the `/app/data -> /secrets` example and the check-then-open race; the `MySandbox` sample (460–525) for the ref, concurrency, cancellation, destruction and exit-code rules and for `ctx.workspace.backend` as a policy-bypassing escape hatch; §"Checking a backend" (526–559) for `WorkspaceBackendSuite`, `attach_backend`, `destroy_environment`, `destructive_backend`, `fresh_backend`, the four boolean fixtures, `-rs` and the 2.x stability promise; §"Third-party workspaces" (436–441) for `pydantic-ai-backend` and its five backends; §"Platforms" (570–588) for the PowerShell conformance claim; §"Limits" (589–595) for the provider-dependent timeout stop. Evidence class: **Reported** — vendor reference documentation naming no version; no backend was written, no suite run, no provider SDK called.
