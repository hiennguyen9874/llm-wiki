---
type: Concept
title: Pydantic AI workspaces and sandboxes
description: ctx.workspace gives Pydantic AI tools one file-and-command API that runs locally or in a sandbox — the sandbox list, read-only and wrapper policies, and the timeout, output and platform limits around it.
tags: [ml, pydantic-ai, agents, sandboxing]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:22:52Z }
stale_after: 2026-12-23
sources:
  - id: dd-v2-tour-2026
    resource: ../raw/pydantic-ai-whats-new-2026/index.md
    scope: ../raw/pydantic-ai-whats-new-2026/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP"
  - id: pydantic-vs-claude-sdk-2026
    resource: ../raw/pydantic-ai-vs-claude-agent-sdk/index.md
    scope: ../raw/pydantic-ai-vs-claude-agent-sdk/
    kind: article
    revision: sha256:e13b086e39460e61065006caca8d0b4b2502621205a283c70cd66ea1da31974b
    title: "Pydantic AI vs Claude Agent SDK: Who owns the agent?"
  - id: pydantic-code-sandboxes
    resource: ../raw/code-mode-vs-sandboxes/index.md
    scope: ../raw/code-mode-vs-sandboxes/
    kind: article
    revision: sha256:8d543df622eaaabd1fbf785550e6492c92479d39aefc1f1a94b9292057a6612b
    title: "Code mode vs sandboxes for AI agents"
  - id: pydantic-dbos-docs
    resource: ../raw/capabilities/durable_execution/dbos/index.md
    scope: ../raw/capabilities/durable_execution/dbos/
    kind: documentation
    revision: sha256:244a04f5850362a7fba71144476c4757655019e142a4e838712ae39035332862
    title: "Durable Execution with DBOS"
  - id: pydantic-workspace-docs
    resource: ../raw/core-concepts/workspace/index.md
    scope: ../raw/core-concepts/workspace/
    kind: documentation
    revision: sha256:106c823ceb0c9563c3569f0dc7dac59f8a7e88365b54f2dc10bc3c3df5c09871
    title: "Workspaces"
---

`ctx.workspace`, added in v2.52.0 on 2026-09-29, gives a tool one API for files and commands regardless of where they run: on the local machine or inside a sandbox. The tool code does not change when the backend changes — swap `LocalWorkspace` for a sandbox and the same `ctx.workspace.run(...)` calls apply[^dd-v2-tour-2026]

## Shape of the API

`LocalWorkspace('.', read_only=False)` is attached as a [capability](pydantic-ai-capability-primitive.md). A tool then awaits `ctx.workspace.run([...], timeout=...)`, receives `exit_code`, `stdout` and `stderr`, and can convert a `WorkspaceError` into `ModelRetry` so the model gets a chance to correct itself[^dd-v2-tour-2026]:

```python
@agent.tool
async def run_tests(ctx: RunContext[object], path: str) -> str:
    """Run pytest on a path and return the tail of the output."""
    try:
        result = await ctx.workspace.run(['python', '-m', 'pytest', '-q', path], timeout=120)
    except WorkspaceError as e:
        raise ModelRetry(f'Could not run tests: {e}') from e
    return f'exit={result.exit_code}\n{result.stdout[-2000:]}'
```

Note the `RunContext[object]` annotation: under v2's generic default, `RunContext[None]` fails strict type checking on an agent without `deps_type`[^dd-v2-tour-2026]

### The method surface

Whatever the environment, `ctx.workspace` has the same methods[^pydantic-workspace-docs]:

- `run`, which runs a command — `cwd='subdir'` starts it in another directory relative to the working directory, which must already exist.
- `read_text`/`write_text` and `read_bytes`/`write_bytes`, where writing creates any missing parent directories.
- `list_dir`, `stat`, `exists`, `make_dir` and `remove` for directories and entries.
- The policy and provider surfaces covered below and in [workspace backends](pydantic-ai-workspace-backends.md): `attached`, `read_only`, `authority_of(path)`, `realpath`, `resolve`, `platform`, `paths` and `backend`.

Relative paths resolve against the workspace's working directory, and that is a starting point rather than a boundary: `..` and absolute paths reach the rest of the environment, and sandbox providers use different default users and working directories, so portable commands prefer relative paths or set `working_dir=`[^pydantic-workspace-docs]

A bad path raises the usual error — `FileNotFoundError`, `IsADirectoryError` — which ends the run unless caught and re-raised as `ModelRetry`; on Temporal it instead follows the activity retry policy. An environment that is gone raises `WorkspaceUnavailableError` and ends the run, while a command killed by a signal in a live environment returns its exit code[^pydantic-workspace-docs]

## Sandbox catalogue

| Added | Backend |
| --- | --- |
| v2.52.0 | `E2BSandbox`, `SpritesSandbox`, `SSHWorkspace`, `BubblewrapSandbox` |
| v2.56.0 | `SmolSandbox`, a local smolvm microVM |
| v2.59.0 | `DaytonaSandbox`, running `Coder`, `Shell`, `FileSystem` and the other Harness capabilities in a Daytona sandbox |
| Harness | A Modal sandbox |

`SSHWorkspace` is the odd entry: it is a remote workspace reached over SSH rather than an isolated sandbox, so "sandbox" in the API name does not imply a security boundary for every backend[^dd-v2-tour-2026]

The workspace documentation lists a wider set without dating the entries: Modal, E2B, Render, Sprites, Daytona, boxd, Kubernetes (`agent-sandbox`), a local smolvm microVM, and self-hosted OpenSandbox servers. It also states when a sandbox comes into existence — on the run's first use of it, which is a tool call or `Coder` loading repository instructions at run start, and at run start for durable runs — and that a run which never used its workspace records no reference, so a method call on `result.workspace` can create a sandbox no message accounts for[^pydantic-workspace-docs]

## Swapping the workspace without touching the agent

The backends are interchangeable at one slot. With the Harness `Coder` attached, `LocalWorkspace(".")` runs its commands on the developer's own machine; replacing it with `ModalSandbox()` from `pydantic_ai_harness.modal_sandbox` runs the same file and shell tools inside a Modal sandbox, and `E2BSandbox()` or `SpritesSandbox()` drop into the same slot[^pydantic-vs-claude-sdk-2026] That the Modal backend imports from the Harness package while the others are core workspace backends matches the catalogue rows above. Tools you write yourself reach the environment through `ctx.workspace`, so a tool tested on a laptop runs in the sandbox unchanged[^pydantic-vs-claude-sdk-2026]

Two operational consequences follow from the same comparison[^pydantic-vs-claude-sdk-2026]:

- **Placement.** The agent itself stays in your application and only its commands and file edits move into the sandbox. The contrasting advice for a bundled coding-agent SDK is to run the whole SDK inside a sandboxed container, which puts the agent in there with the tools.
- **Cleanup.** A sandbox keeps running after the run ends, so it has to be deleted explicitly; nothing in the swap deletes it for you.

## Read-only access and policy wrappers

`read_only=True` lets tools read and list files while refusing commands and changes, because a command could change files; a refused change raises `WorkspaceReadOnlyError`, and a capability can check `ctx.workspace.read_only` to leave its write tools out[^pydantic-workspace-docs]

Two other routes exist for a single run: wrap the workspace in `ReadOnlyWorkspace` and pass it as `workspace=` — the reviewer in [workspace selection](pydantic-ai-workspace-selection.md) does exactly that — or write your own policy by subclassing `WrapperWorkspace`, overriding the operations to change and calling `self.wrapped` for the rest[^pydantic-workspace-docs]

`run()` bypasses file-method policies unless the wrapper also overrides or refuses commands, which is why the source's `RootedWrites` example replaces both a file method and `run`. Its write check compares the `realpath` of the workspace root with the `realpath` of the resolved target, and it is a preflight rather than a security boundary against concurrent symlink changes: for untrusted commands the source sends you to an isolated backend, not to path checks[^pydantic-workspace-docs]

## Choosing the boundary

**Reported, Pydantic AI and Harness version unspecified:** a sandbox can contain the whole agent, only workspace tools, or only model-written code in Monty. A whole-agent sandbox also contains credentials the agent needs unless a separate proxy supplies them. A sandbox workspace keeps the agent and its credentials outside while file and command tools work inside; it can be combined with [code mode](pydantic-ai-code-mode.md) to isolate the model program separately.[^pydantic-code-sandboxes]

The vendor describes `LocalWorkspace` as **not a sandbox**: commands run as the local user and the directory is only their starting location. It reports a restricted inherited environment (`PATH`, `HOME`, and locale variables), not filesystem or user isolation. It describes `SSHWorkspace` as remote but not isolated, and `BubblewrapSandbox` as read-only host with writable working directory and no network by default, suitable against accidents rather than hostile agents. Verify actual configuration and version before relying on these boundaries.[^pydantic-code-sandboxes]

The article reports that passing a run's message history to the next run continues the same sandbox and its files and installed packages. It warns that the framework does not delete the sandbox automatically: it can continue billing until explicitly destroyed or the provider's lifetime limit ends it. Provider cleanup details are not given.[^pydantic-code-sandboxes]

## Interaction with durable execution

Workspaces work under durable execution. Under DBOS, each workspace call made in workflow code becomes a step — including calls from function tools, which DBOS runs in workflow code — and a run with a workspace executes its tool calls sequentially, except for tools in a child workflow, whose workspace calls belong to the child and still run in parallel[^dd-v2-tour-2026][^pydantic-dbos-docs] That sequencing is a real performance consequence for tools that could otherwise run in parallel, and it follows from replay requiring a deterministic order. Two further DBOS costs come from history: workflow-side workspace arguments (commands, `env=`, file contents) are stored in the database, so secrets belong in the workspace capability's `env=` rather than passed to a call and stored history should sit behind a payload codec; and adding a workspace to an agent changes its steps, so in-flight workflows must drain or the change must deploy as a new application version[^pydantic-dbos-docs] Under Temporal the workspace moves further — a tool sees it rebuilt inside an activity, a workflow-side call becomes an activity of its own, and every worker needs the same capabilities and directory — see [Pydantic AI on Temporal](pydantic-ai-temporal.md).

Four further rules apply inside a workflow or flow[^pydantic-workspace-docs]:

- The environment is created or attached at run start even if no tool uses it, and without an explicit `run_id` the run derives one from the engine's execution id, so the workspace stays addressable after a worker restart. A worker that dies after creating the environment but before recording it can leave a second sandbox behind, which the provider's own tools have to clean up.
- A run-level `workspace=` passes only a reference, and the run rebuilds the workspace from the agent's own capabilities. A policy wrapper such as `ReadOnlyWorkspace(...)` or `AuthorityWorkspace(...)` raises `UserError` because rebuilding would drop it, and so does a live backend with no reference or a run-level capability that changes the workspace's type; other run-level settings such as a sandbox image do not apply at all. The policy belongs on the agent's capability instead — `LocalWorkspace(..., read_only=True)` or `LocalWorkspace(..., authority='none')`.
- `workspace.backend` is not available in workflow code, which includes DBOS function tools and tools opted out of their durable unit, and the deprecated `TemporalAgent`, `DBOSAgent` and `PrefectAgent` wrappers refuse a workspace outright.
- Temporal bounds a command by the activity's `start_to_close_timeout`, 60 seconds by default, whatever the command's own `timeout` — raise it through `metadata={'temporal': ActivityConfig(...)}`. On Temporal and Prefect, workspace timeouts, output-limit failures, read-only refusals and a lost environment are never retried, while other exceptions follow the retry policy, which on Temporal retries without limit by default: catch them and raise `ModelRetry`, or bound them with `maximum_attempts`.

## Side effect: Anthropic token defaults

The same v2.52.0 release raised `AnthropicModel`'s default `max_tokens` on Claude Sonnet 4.5 and later, first to 16384 and then to the model's maximum output, streaming those requests behind the scenes. Anyone who relied on the old 4096 default to cap spend must now set `max_tokens` explicitly[^dd-v2-tour-2026]

## Timeouts, output and the host

- `run(timeout=...)` starts its clock after the sandbox is ready — locally, after resolving the working directory — and local process startup counts as command time. The deadline covers the command only, `timeout=None` removes it entirely, and a provider's own sandbox lifetime and idle limits are separate. On its deadline the foreground command is stopped and `WorkspaceTimeoutError` carries the partial `stdout` and `stderr`[^pydantic-workspace-docs]
- Commands receive stdin at EOF, so an interactive prompt fails instead of waiting; non-interactive flags such as `-y` are the documented answer[^pydantic-workspace-docs]
- A local command whose combined output exceeds 10 MiB raises `WorkspaceOutputLimitError`, with the first 64 KiB of each stream kept in `stdout` and `stderr`[^pydantic-workspace-docs]
- The local backend and the command-backed shell fallback require POSIX. On Windows, `WindowsWorkspace` takes the same options, runs commands in PowerShell (`pwsh` when it is on `PATH`, else Windows PowerShell) with Windows paths, wraps each command in a Job Object so a timeout or cancellation ends the processes it started, and passes only the variables Windows tools need plus `env=`[^pydantic-workspace-docs]
- A backend whose shell and paths are not POSIX declares that through `SupportsPlatform`, and tools read `Workspace.platform` and `Workspace.paths` (`posixpath` or `ntpath`) instead of assuming a shell[^pydantic-workspace-docs]
- Local background jobs outlive `run()`, so redirecting their output avoids the two-second drain grace when they inherit `stdout` or `stderr`; the caller cleans them up when the host exits[^pydantic-workspace-docs]

## Security choices

`LocalWorkspace` has the full authority of the host user, and neither `working_dir` nor a Harness `FileSystem` root jails shell commands. Commands inherit `PATH`, `HOME`, `LANG`, `LC_ALL` and `LC_CTYPE` plus whatever `env=` adds — never `os.environ`, which would hand the model's commands the application's API keys. Under durable execution, workflow-side workspace arguments including `env=` and file contents are stored in durable history, so secrets there need a payload codec. Agent run spans record `pydantic_ai.workspace.id` — the sandbox id, or the directory path for `LocalWorkspace` — even with `include_content=False`, because it identifies the environment rather than content[^pydantic-workspace-docs]

## Limits

- No workspace or sandbox was executed in this ingest; the article's example was type-checked and run against `TestModel`, which exercises no filesystem[^dd-v2-tour-2026]
- The vendor article reports selected default isolation properties above, but resource limits, full network policies, credential exposure and hostile-code resistance across backends remain unverified. It names no Pydantic AI or Harness version; no commands or sandboxes were run.[^pydantic-code-sandboxes]
- The sequential-tool-call behaviour under DBOS is the article's reading of the DBOS docs, now corroborated by the DBOS reference page's own statement of the workspace sequencing and its child-workflow exception; both are vendor material and no run was observed[^pydantic-dbos-docs]
- The swap-and-cleanup description comes from a vendor comparison that names no Pydantic AI release version, gives no cost, lifetime or deletion API, and was not executed here[^pydantic-vs-claude-sdk-2026]
- The method surface, error types, read-only and wrapper policies, timeout and output limits, `WindowsWorkspace` behaviour and the `pydantic_ai.workspace.id` attribute come from Pydantic's own workspace documentation, which names no release version and reports no measurement; none of those paths was exercised here, so the added claims are **Reported**[^pydantic-workspace-docs]

## Relationships

- **Related to** [E2B sandbox recovery](pydantic-ai-e2b-sandbox-recovery.md): an E2B-specific pause, resume and Temporal recovery example.

- **Composes with** [Pydantic AI code mode](pydantic-ai-code-mode.md): workspace tools and model-written code can have separate isolation boundaries.[^pydantic-code-sandboxes]
- **Uses** the [capability primitive](pydantic-ai-capability-primitive.md): `LocalWorkspace` is a core capability.
- **Depends on** [durable execution](pydantic-ai-durable-execution.md) for step-level replay of workspace calls.
- **Explained call site by call site in** [Pydantic AI durable tool placement](pydantic-ai-durable-tool-placement.md): where a tool runs under an engine, and which tool definitions can still opt out.
- **Is moved off the workflow process by** [Pydantic AI on Temporal](pydantic-ai-temporal.md): the activity rebuild, per-worker parity, shared absolute paths and the history exposure of `env=` and file contents.
- **Stays in process under** [Pydantic AI on DBOS](pydantic-ai-dbos.md): a workspace call is one step of the same run, sequential tool calls are the cost, and workflow-side arguments land in the system database.[^pydantic-dbos-docs]
- **Related to** [Pydantic AI run controls](pydantic-ai-run-controls.md): explicit timeouts and token ceilings bound the same spend-and-latency problem.
- **Chosen by** [Claude Agent SDK versus Pydantic AI](claude-agent-sdk-vs-pydantic-ai.md) as the mechanism that keeps the agent in process while moving model-written commands off the host.
- **Is selected, resumed and cleaned up through** [workspace selection](pydantic-ai-workspace-selection.md): the `workspace=` override, the `WorkspaceRef` the messages carry, and the `on_run_error` deletion this page's cleanup note assumes.
- **Carries the provenance read by** [workspace file authority](pydantic-ai-workspace-authority.md), which records the `authority` and `path_authority` levels a capability applies when it puts workspace text in the prompt.
- **Delegates the provider side to** [workspace backends](pydantic-ai-workspace-backends.md): the backend contract a sandbox implements, what `realpath` can and cannot answer, and the conformance suite that checks it.
- **Is supplied by** two Harness sandbox capabilities at integration depth: [Modal](pydantic-ai-harness-modal-sandbox.md) (24-hour default, never terminated by Pydantic AI, network reachable) and [E2B](pydantic-ai-harness-e2b-sandbox.md) (pauses instead of dying, Hobby-hour limit, token-injecting proxy). Both register no tools.

[^pydantic-code-sandboxes]: Marcelo Trylesinski, [Code mode vs sandboxes for AI agents](../raw/code-mode-vs-sandboxes/index.md), Pydantic, 2026-11-10, “Where the sandbox boundary goes”, “Workspaces in Pydantic AI”, and “Code mode and a workspace together”. **Reported:** vendor source; local SVG diagrams repeat text and alt text, while external links and embedded traces were not fetched; no code was executed.
[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"Workspaces: one API for local and sandboxed tools (v2.52)" (raw lines 330–357) for `ctx.workspace`, the `LocalWorkspace` capability, the `run_tests` sample, the sandbox list, the DBOS sequencing note, and the Anthropic `max_tokens` change; §"What changed in v2.58 and v2.59" for `DaytonaSandbox`. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — article-level description with an author-run `TestModel` sample; no sandbox, filesystem, or provider call was exercised here.
[^pydantic-vs-claude-sdk-2026]: Aditya Vardhan, "Pydantic AI vs Claude Agent SDK: Who owns the agent?", Pydantic, published 2026-10-05, §"Give it somewhere to work" (raw lines 102–119) for `LocalWorkspace(".")` running commands as the developer, the `ModalSandbox()`/`E2BSandbox()`/`SpritesSandbox()` slot, `ctx.workspace` for hand-written tools, the note that only commands and edits move, the container-sandboxing contrast with the Claude Agent SDK, and sandbox deletion. Local capture: `raw/pydantic-ai-vs-claude-agent-sdk/index.md`, content digest sha256:e13b086e. Evidence class: **Reported** — vendor comparison; nothing was executed.
[^pydantic-dbos-docs]: Pydantic, "Durable Execution with DBOS" (pydantic.dev docs, `/docs/ai/capabilities/durable_execution/dbos/`), 4,754 words as declared, no version or date stated; local capture `raw/capabilities/durable_execution/dbos/index.md`, content digest sha256:244a04f5. §"Workspaces" (raw lines 193–200) for each workspace call as a step, the child-workflow exception, workflow-side arguments stored in history, the `env=` advice, the payload codec and the step-changing redeploy rule; §"Parallel Tool Execution" (322–327) for sequential tool calls in a workspace run and parallel child-workflow tools. Evidence class: **Reported** — vendor reference page naming no version; no workspace, sandbox or command was run.

[^pydantic-workspace-docs]: Pydantic, "Workspaces" (pydantic.dev docs, `/docs/ai/core-concepts/workspace/`), 6,000 words as declared, 6,040 by local `wc -w`, no version, author or date stated; local capture `raw/core-concepts/workspace/index.md`, content digest sha256:106c823e. §"Give an agent an environment" (raw lines 12–50) for `ctx.workspace.run`, the exit-code/stdout/stderr result, `cwd=` and the `WorkspaceError` to `ModelRetry` advice; §"Move it into a sandbox" (51–65) for the wider sandbox set, when a sandbox is created and the unrecorded-sandbox warning; §"Your machine or a sandbox" (143–158) for the inherited `PATH`/`HOME`/locale variables and the `env=` rule; §"Using the workspace in tools" (159–192) for the method list, parent-directory creation, relative paths as a starting point, and the error and signal behaviour; §"Read-only access" (193–226) for `read_only=True`, `WorkspaceReadOnlyError`, `ReadOnlyWorkspace`, `WrapperWorkspace`, the `run()` bypass and `RootedWrites`; §"Durable execution" (329–383) for run-start attach, the derived run id and leftover sandbox, the reference-only `workspace=` with its `UserError` cases, the unavailable `workspace.backend`, the refusing deprecated wrappers, and the activity `start_to_close_timeout` and retry exceptions; §"Timeouts and clocks" (560–563) for the clock start, stdin at EOF and partial output; §"Security choices" (564–569) for host authority, the `os.environ` warning, durable-history arguments and `pydantic_ai.workspace.id`; §"Platforms" (570–588) for the 10 MiB output limit, the POSIX requirement, `WindowsWorkspace`, the Job Object, `SupportsPlatform` and local background jobs. Evidence class: **Reported** — vendor reference documentation naming no version; no workspace, sandbox, command or trace was exercised here.
