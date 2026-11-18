---
title: "E2B Sandbox"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/harness/e2b-sandbox/"
domain: "pydantic.dev"
language: "en"
description: "Run a Pydantic AI agent's commands and file edits in an isolated E2B cloud sandbox instead of on your machine."
word_count: 4125
---

Run your agent’s commands and file edits in an isolated [E2B](https://e2b.dev/) cloud sandbox instead of on your machine.

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/e2b_sandbox/)

> While Pydantic AI Harness is on 0.x releases, the API may change between minor releases; when it does, deprecation warnings and release-note migration guidance tell you (or your agent) exactly how to upgrade. See the [version policy](https://pydantic.dev/docs/ai/harness/#version-policy).

```
flowchart TB
    accTitle: E2B Sandbox: your agent's commands run in an E2B cloud sandbox
    accDescr: On your machine, the model calls Coder, Shell or FileSystem tools such as run_command. Via ctx.workspace, E2BSandbox's get_workspace gives the run an E2B cloud sandbox over the E2B API with E2B_API_KEY, paused at its timeout and killed by destroy(ref). A later run reattaches with the WorkspaceRef in the message history or result.workspace.ref and resumes the sandbox if paused.
    subgraph machine["Your machine"]
        model(["model"])
        tools["Coder, Shell or<br/>FileSystem tools,<br/>such as run_command"]
        ref["WorkspaceRef<br/>in the message history,<br/>result.workspace.ref"]
        e2b["E2BSandbox()<br/>get_workspace gives<br/>the run an E2B sandbox"]:::capability
    end
    sandbox["E2B cloud sandbox<br/>paused at its timeout,<br/>killed by destroy(ref)"]:::external
    model <-->|"tool call, result"| tools
    tools -->|"ctx.workspace"| e2b
    ref -.->|"a later run reattaches<br/>and resumes it if paused"| e2b
    e2b <-->|"E2B API, E2B_API_KEY"| sandbox
    classDef capability stroke:#E520E9,stroke-width:2px
    classDef external stroke:#0E9C86,stroke-width:2px
```

## Install

- [pip](#tab-panel-0-0)
- [uv](#tab-panel-0-1)

Terminal

```bash
pip install "pydantic-ai-harness[coder,e2b,anthropic]"
```

The `coder` extra is there because the examples use `Coder`; the sandbox itself doesn’t need it. The `anthropic` extra is there because the examples use an Anthropic model; swap it for your model provider’s extra. Then set `E2B_API_KEY` to your E2B API key, and `ANTHROPIC_API_KEY` for the examples.

## Quick start

```python
from pydantic_ai import Agent
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.e2b_sandbox import E2BSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[E2BSandbox(), Coder()])
result = agent.run_sync('Clone https://github.com/pydantic/pydantic-ai and summarize how capabilities work.')
```

`Coder`’s shell and file tools now run in the sandbox, not on your machine. With `Coder`, `RepoContext` creates the sandbox when the run starts, even without a tool call; use `Coder(repo_context=False)` for lazy creation. It keeps running, and billing, after the run ends; see [Clean up](#clean-up).

A sandbox lives for 1 hour (`sandbox_timeout=3600`, the most E2B’s Hobby plan allows), then pauses; the next run resumes it. Pro plans allow up to `E2BSandbox(sandbox_timeout=86400)`. A lifetime over your plan’s limit raises `WorkspaceUnavailableError`, with the limit in the message.

Commands start in the home directory, `/home/user`, which holds dotfiles and the pip cache. Pass a project directory, such as `E2BSandbox(working_dir='/home/user/project')`, so the project is not the home directory; it is created for you on a new sandbox.

E2B’s default template does not include ripgrep (`rg`). `Coder` can search without it, but installing `rg` makes searches faster. Build a reusable [template](https://e2b.dev/docs/template/quickstart) once, outside an agent run (building can take a minute):

```
from e2b import AsyncTemplate, Template
await AsyncTemplate.build(Template().from_base_image().apt_install(['ripgrep']), 'my-rg-template')
agent = Agent('anthropic:claude-opus-5-5', capabilities=[E2BSandbox(template='my-rg-template'), Coder()])
```

The default template has Python and git but not your project’s dependencies, not even pytest. Install them in a custom template, or with `await workspace.run(['pip', 'install', ...])` before the run, as in [Prepare a sandbox before the run](#prepare-a-sandbox-before-the-run).

## Continue in the same sandbox

```python
from pydantic_ai import Agent
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.e2b_sandbox import E2BSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[E2BSandbox(), Coder()])
result = agent.run_sync('Clone https://github.com/pydantic/pydantic-ai and summarize how capabilities work.')

followup = agent.run_sync(
    'Which capability would you add next, and where would it live?',
    message_history=result.all_messages(),
)
```

The follow-up run finds the sandbox in the message history and works in it, so the clone is still there. Without the history, a run starts a new sandbox. A paused sandbox resumes. If the sandbox has been killed, the run raises `WorkspaceUnavailableError` instead of starting over in an empty one.

## Choose the tools

For a narrower agent, use [`Shell`](https://pydantic.dev/docs/ai/harness/shell/) and [`FileSystem`](https://pydantic.dev/docs/ai/harness/filesystem/) instead of `Coder`, or write your own tool:

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai_harness.e2b_sandbox import E2BSandbox
from pydantic_ai_harness.file_system import FileSystem
from pydantic_ai_harness.shell import Shell

agent = Agent('anthropic:claude-opus-5-5', capabilities=[E2BSandbox(), Shell(), FileSystem()])

@agent.tool
async def run_python(ctx: RunContext, code: str) -> str:
    """Run a Python snippet in the sandbox."""
    result = await ctx.workspace.run(['python', '-c', code], timeout=10)
    return result.stdout + result.stderr
```

Shell commands run as the `user` account, and files the backend creates are owned by it. E2B’s file service still reads and writes with its own root privileges, so Unix permissions do not restrict file operations; do not rely on them to keep file tools out of a path.

Reading a FIFO raises `OSError` instead of waiting for a writer. E2B’s file API leaves looping symlinks out of directory listings.

A background child that inherits stdout or stderr can keep `run()` waiting for the SDK stream to close after the main command exits. Redirect background output to a file when starting a long-running job; `Shell.start_command` manages its own output log.

### What a timeout stops

On a timeout or cancellation, the backend sends TERM, then KILL, to the command’s process group, which includes its children unless they move to another process group or session. Custom templates need `/bin/bash` and `/bin/sh`; without `setsid` (util-linux), only the command’s own process is stopped. The sandbox keeps running. Stopping is best effort: if E2B cannot be reached, the command may keep running, so keep the ref to inspect or kill the sandbox.

A command whose combined output passes 10 MiB is stopped the same way and raises `WorkspaceOutputLimitError`, with the first 65,536 characters of each stream in `stdout` and `stderr`. Redirect large output to a file instead.

A command killed by a signal may return `exit_code=-1` in E2B; the SDK does not identify the signal, so this is not converted to `128+signal`.

Concurrent writes to the same path are not atomic on E2B: uploads may interleave, and a reader can see a partial file. Coordinate writers or write to separate paths when using `FileSystem` or `Coder`.

See [Workspaces](https://pydantic.dev/docs/ai/core-concepts/workspace/) for more.

## Reattach later

To come back to the sandbox without the message history, store the run’s workspace ref and pass it back as `workspace=`:

```python
from pydantic_ai import Agent
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.e2b_sandbox import E2BSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[E2BSandbox(), Coder()])

result = agent.run_sync('Clone https://github.com/pydantic/pydantic-ai and summarize how capabilities work.')
ref = result.workspace.ref  # store this, e.g. in your database

later = agent.run_sync('Which capability would you add next, and where would it live?', workspace=ref)
```

The ref holds no credentials, so the process that reattaches needs them too. Pass `workspace='new'` to start a fresh sandbox even when the message history names one.

`template`, `allow_internet_access` and `network` only shape a new sandbox. `sandbox_timeout` also applies when you reattach, and `working_dir` and `env` apply to every command.

Already have an `e2b.AsyncSandbox`? Pass `workspace=E2BSandboxBackend(sandbox=sandbox)` to a run, with `E2BSandboxBackend` from `pydantic_ai_harness.e2b_sandbox`. `E2BSandbox`’s settings don’t apply to it; pass `working_dir=` and `env=` to the backend.

## Use different credentials for each user

`E2BSandbox(client=E2B(api_key=...))` sets one client for the capability, in place of `E2B_API_KEY` and the rest of the environment. The environment holds one key for the whole process, so it can’t serve several users at once. When each user has their own E2B account, supply the workspace from a capability of your own, which builds the client from the run’s `deps`:

```python
from dataclasses import dataclass

from e2b import E2B
from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.workspaces import WorkspaceBackend, WorkspaceRef
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.e2b_sandbox import E2BSandboxBackend

@dataclass
class User:
    e2b_api_key: str

@dataclass
class UsersE2B(AbstractCapability[User]):
    def get_workspace(self, ctx: RunContext[User], *, ref: WorkspaceRef | None) -> WorkspaceBackend | None:
        if ref is not None and ref.provider != 'e2b':
            return None
        if not ctx.deps.e2b_api_key:  # E2B would fall back to `E2B_API_KEY`
            raise ValueError('This user has no E2B API key.')
        return E2BSandboxBackend(client=E2B(api_key=ctx.deps.e2b_api_key), ref=ref)

agent = Agent('anthropic:claude-opus-5-5', deps_type=User, capabilities=[UsersE2B(), Coder()])
```

E2B’s client falls back to `E2B_API_KEY` when its key is empty or `None`. If that variable is set where your app runs, a user with no key would run on that account, so check for a key before building the client, as above.

Under [Temporal](https://pydantic.dev/docs/ai/capabilities/durable_execution/temporal/), `deps` are serialized for every activity, which puts a key on them in the workflow’s history. Put a user ID there instead, and have `get_workspace` look that user’s key up on the worker. A client itself can’t be on `deps` there at all.

Destroy a user’s sandbox with that user’s key, as in `await E2BSandbox(client=E2B(api_key=user.e2b_api_key)).destroy(ref)`. A client for another account may not find the sandbox, and a sandbox that isn’t found returns quietly, so it would keep running and billing with no error.

## Prepare a sandbox before the run

To seed files or install packages before the agent starts, create the backend yourself, work in it through `Workspace`, and pass it to the run:

```python
import asyncio

from pydantic_ai import Agent
from pydantic_ai.workspaces import Workspace
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.e2b_sandbox import E2BSandbox, E2BSandboxBackend

agent = Agent('anthropic:claude-opus-5-5', capabilities=[E2BSandbox(), Coder()])

async def main() -> None:
    backend = E2BSandboxBackend(working_dir='/home/user/project')
    try:
        workspace = Workspace(backend)
        await workspace.write_text('calc.py', 'def add(a, b):\n    return a - b\n')
        install = await workspace.run(['pip', 'install', 'pytest'], timeout=300)
        if install.exit_code != 0:
            raise RuntimeError(f'pip install failed: {install.stderr}')
        result = await agent.run('Fix the bug in calc.py.', workspace=backend)
        print(result.output)
    finally:
        ref = backend.ref  # set once the sandbox exists
        if ref is not None:
            await E2BSandbox().destroy(ref)

if __name__ == '__main__':
    asyncio.run(main())
```

The `finally` kills the sandbox even when setup or the run fails. To keep it instead, store `backend.ref` and pass it as `workspace=` to reattach later.

## Keep a token out of the sandbox

Pass `network` to have E2B add a token to the sandbox’s requests itself, so the token is never inside the sandbox. `network` takes E2B’s own network options and passes them on unchanged. Here `gh` and `git push` work as the token’s owner, while `echo $GH_TOKEN` in the sandbox prints `placeholder`:

```python
import base64

from pydantic_ai_harness.e2b_sandbox import E2BSandbox

token = '...'  # a GitHub token, such as the output of `gh auth token`
basic = base64.b64encode(f'x-access-token:{token}'.encode()).decode()
sandbox = E2BSandbox(
    env={'GH_TOKEN': 'placeholder'},  # `gh` sends a token only when one is set; the proxy replaces it
    network={
        'rules': {
            'github.com': [{'transform': {'headers': {'Authorization': f'Basic {basic}'}}}],  # git over HTTPS
            'api.github.com': [{'transform': {'headers': {'Authorization': f'token {token}'}}}],  # gh
            'uploads.github.com': [{'transform': {'headers': {'Authorization': f'token {token}'}}}],
        }
    },
)
```

E2B adds the header as each request leaves the sandbox, replacing any header with the same name. E2B calls this [public beta](https://docs.e2b.dev/sandbox/internet-access), so it may change.

- Only HTTPS requests get the header. Use `https://` remotes, not `git@github.com:owner/repo.git`.
- If you also set `allow_out` or `allow_internet_access=False`, add each host in `rules` to `allow_out`, or its requests are blocked.
- The agent can’t see the token, but it can use it for anything the token allows.
- List only hosts that never send request headers back in a response, or a command could read the token there.
- An attached sandbox keeps its rules. To change them, for example to swap the token, call `update_network` on `await backend.get_sandbox()`. It replaces all network options at once.
- To keep the token out of the request that creates the sandbox too, save the whole header value as an E2B secret and use `e2b.Secret.fill(name)` as the value.

## Preview a dev server

With `Shell`, ask the agent to use `start_command` for `npm run dev -- --host 0.0.0.0 --port 3000`, then poll `check_command` and `curl http://localhost:3000/health` until ready. Save the returned command ID. Given the workspace ref, get the sandbox with `sandbox = await capability.backend(ref).get_sandbox()`, where `capability` is the `E2BSandbox` the agent runs with, so its `sandbox_timeout` applies, and use `sandbox.get_host(3000)` for the public hostname (prefix with `https://` for the preview URL). When done, call `stop_command` with the ID while the workspace is attached, then delete the sandbox with `await E2BSandbox().destroy(ref)`. Do not leave a public preview running longer than necessary.

## Clean up

The sandbox keeps running, and billing, after the run ends. Pydantic AI does not kill it. If a run is cancelled while E2B creates the sandbox, the ref is still recorded once E2B answers; the id is also logged (see [Telemetry](#telemetry)). If E2B’s answer never arrives, the sandbox can exist with no ref or log entry; find and kill it in the E2B dashboard. Kill the others with the ref you stored:

```python
from pydantic_ai.workspaces import WorkspaceRef
from pydantic_ai_harness.e2b_sandbox import E2BSandbox

async def kill_sandbox(ref: WorkspaceRef) -> None:
    await E2BSandbox().destroy(ref)
```

`E2BSandbox.backend(ref)` constructs an attached backend without I/O; `destroy(ref)` kills by ID with the instance’s `client`, without attaching. This kills a paused sandbox too, without resuming it. A sandbox you don’t kill is paused when its `sandbox_timeout` runs out. See [E2B’s sandbox lifecycle](https://docs.e2b.dev/sandbox).

A failed run returns no result, so there is no ref to store. To terminate its sandbox, clean up in an `on_run_error` hook; `after_run` doesn’t run when a run fails:

```python
from typing import Any

import anyio

from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import Hooks
from pydantic_ai.run import AgentRunResult
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.e2b_sandbox import E2BSandbox

hooks = Hooks()

@hooks.on.run_error
async def terminate_failed_run(ctx: RunContext[None], *, error: BaseException) -> AgentRunResult[Any]:
    if ctx.workspace.ref is not None:
        # Shielded, so an `anyio` deadline around the run doesn't cut the kill short,
        # and bounded, so a hung API call can't hang the run indefinitely.
        with anyio.move_on_after(30, shield=True):
            await E2BSandbox().destroy(ctx.workspace.ref)
    raise error

agent = Agent('anthropic:claude-opus-5-5', capabilities=[E2BSandbox(), Coder(), hooks])
```

## Configuration

| Option | What it does |
| --- | --- |
| `client` | An `e2b.E2B`, for its API key and other connection settings. Default: `None`, `E2B_API_KEY` and the rest of the environment. See [Use different credentials for each user](#use-different-credentials-for-each-user). |
| `template` | E2B template name or ID for a new sandbox. Default: `None`, E2B’s `base`. An unknown template fails on first use. |
| `allow_internet_access` | Whether a new sandbox can reach the internet. Default: `True`. |
| `sandbox_timeout` | Seconds the sandbox lives before E2B pauses it, set on create and on reattach. Default: `3_600` (1 hour, the most E2B’s Hobby plan allows). |
| `working_dir` | Absolute directory commands start in and relative paths resolve against. Default: `None`, the sandbox’s own (`/home/user` on the default template, where commands run as `user`); prefer relative paths or set `working_dir` for portable code. Created on a new sandbox; on an attached or caller-supplied sandbox it must already exist. |
| `env` | Environment variables every command gets. Default: `None`. Output is decoded as UTF-8 either way; the default template’s locale is POSIX, so pass `env={'LC_ALL': 'C.UTF-8'}` if a tool such as `wc -m` should count characters rather than bytes. Nothing from your machine’s environment reaches the sandbox. The agent’s commands can read these values, and a new sandbox keeps them for every process, so leave out secrets the agent should not see. |
| `authority` | The [authority](https://pydantic.dev/docs/ai/core-concepts/workspace/#workspace-authority) of the sandbox’s files: `'none'` for files nobody on your side wrote, such as a cloned third-party repository, `'user'` for the user’s own. The workspace reports it through `authority_of`, and a capability that checks it sends a file’s text to the model with no more authority than that. Default: `'operator'`. |
| `path_authority` | Levels for some directories and files, overriding `authority` for the paths under them; the longest matching path wins. Paths are sandbox paths, relative to the working directory or absolute; `~` isn’t expanded. Default: `None`. |
| `network` | E2B’s network options for a new sandbox, passed to `Sandbox.create` unchanged. Default: `None`. See [Keep a token out of the sandbox](#keep-a-token-out-of-the-sandbox). A spec cannot set it. |

`E2BSandbox` needs asyncio: the E2B SDK runs every request on asyncio, so under Trio every operation, including `destroy`, raises `UserError` before it reaches E2B.

## Durable execution

Install the `temporal` extra too:

- [pip](#tab-panel-1-0)
- [uv](#tab-panel-1-1)

Terminal

```bash
pip install "pydantic-ai-harness[coder,e2b,anthropic,temporal]"
```

Run a Temporal dev server on `localhost:7233` first. The agent and workflow must be defined at module level for activity registration.

```python
import asyncio
import uuid

from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import PydanticAIPlugin, PydanticAIWorkflow, TemporalDurability
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.e2b_sandbox import E2BSandbox
from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker

agent = Agent(
    'anthropic:claude-opus-5-5',
    name='e2b_coder',
    capabilities=[E2BSandbox(), Coder(), TemporalDurability()],
)

@workflow.defn
class SandboxWorkflow(PydanticAIWorkflow):
    __pydantic_ai_agents__ = [agent]

    @workflow.run
    async def run(self, prompt: str) -> str:
        return (await agent.run(prompt)).output

async def main() -> None:
    client = await Client.connect('localhost:7233', plugins=[PydanticAIPlugin()])
    async with Worker(client, task_queue='sandbox', workflows=[SandboxWorkflow]):
        print(
            await client.execute_workflow(
                SandboxWorkflow.run, 'Use the shell tool to run pwd.',
                id=f'sandbox-{uuid.uuid4()}', task_queue='sandbox',
            )
        )

if __name__ == '__main__':
    asyncio.run(main())
```

Removing a capability while workflows using it are still running changes their replay history. Drain those workflows or use [Temporal worker versioning](https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning) before deploying the change.

## Telemetry

`E2BSandbox` emits no spans of its own. Core’s [instrumentation](https://pydantic.dev/docs/ai/capabilities/instrumentation/) records the sandbox on the agent run span as `pydantic_ai.workspace.provider` and `pydantic_ai.workspace.id`, and each command or file operation a tool makes runs inside that tool call’s span; operations at run start, such as `RepoContext` loading repo instructions, run in the agent run span. Creating a sandbox also logs `Created E2B sandbox <id>` at INFO on the `pydantic_ai_harness.e2b_sandbox._backend` logger, so the id is on record even if the run ends before it is stored.

- [Run Pydantic AI coding agents in E2B sandboxes](https://pydantic.dev/articles/pydantic-ai-e2b-sandboxes) (Pydantic): a coding agent in an E2B sandbox

## API reference

### E2BSandbox

**Bases:** `AbstractCapability[AgentDepsT]`

Supply an isolated [E2B](https://e2b.dev/) sandbox as the run’s workspace.

A run with no reference creates a fresh sandbox. Pass a `WorkspaceRef` supplied by the application to attach to an environment managed elsewhere.

This capability supplies execution only. Compose it with tools or capabilities that use the workspace, such as `Coder`, `Shell`, or `FileSystem`. Shell commands run under `sh -c` in the sandbox’s login shell environment.

#### Attributes

##### client

An `e2b.E2B` to create, attach and destroy with, for its API key and other connection settings; `E2B_API_KEY` and the rest of the environment when `None`. A spec cannot set it.

To use different credentials for each user, supply the workspace from a capability of your own, which can build the client from the run’s `deps` and pass it to `E2BSandboxBackend`.

**Type:** `e2b.E2B` | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### template

E2B template name or ID for a newly created sandbox; E2B’s default when `None`.

An unknown template raises `WorkspaceUnavailableError` on first use.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### allow\_internet\_access

Whether a newly created workspace may reach the internet.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `True`

##### sandbox\_timeout

Total lifetime of the sandbox in seconds, applied on create and on attach.

When it runs out, E2B pauses the sandbox and attaching resumes it. The default, 1 hour, is the most E2B’s Hobby plan allows; Pro plans allow up to 86400.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int) **Default:** `DEFAULT_SANDBOX_TIMEOUT`

##### working\_dir

Absolute directory commands start in and relative paths resolve against; `None` uses the sandbox’s own.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### env

Environment variables every command gets, also on an attached workspace; nothing is read from the host.

The agent’s commands can read them, and a new sandbox keeps them for every process it runs.

**Type:** [`Mapping`](https://docs.python.org/3/library/typing.html#typing.Mapping) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)\] | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `field(default=None, repr=False)`

##### authority

The [authority](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.Authority) of the sandbox’s files: `'none'` for files nobody on the application’s side wrote, such as a cloned third-party repository, and `'user'` for the user’s own files. Anything below `'operator'` wraps the workspace in an [`AuthorityWorkspace`](https://pydantic.dev/docs/ai/api/pydantic-ai/workspaces/#pydantic_ai.workspaces.AuthorityWorkspace).

**Type:** [`Authority`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.Authority) **Default:** `'operator'`

##### path\_authority

Levels for some directories and files, overriding `authority` for the paths under them; the longest matching path wins. Paths are sandbox paths: relative ones resolve against the working directory, and `~` isn’t expanded. See [`Workspace.authority_of`](https://pydantic.dev/docs/ai/api/pydantic-ai/workspaces/#pydantic_ai.workspaces.Workspace.authority_of).

**Type:** [`Mapping`](https://docs.python.org/3/library/typing.html#typing.Mapping) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Authority`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.Authority)\] | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### network

E2B’s network options for a new sandbox, passed to `Sandbox.create` unchanged; a spec cannot set them.

Their `rules` have E2B add headers, such as a token, to requests as they leave the sandbox, so commands can use the token without it ever being inside the sandbox.

**Type:** `SandboxNetworkOpts` | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `field(default=None, repr=False)`

#### Methods

##### from\_spec

`@classmethod`

```python
def from_spec(
    cls,
    *,
    id: str | None = None,
    description: str | None = None,
    defer_loading: bool = False,
    template: str | None = None,
    allow_internet_access: bool = True,
    sandbox_timeout: int = DEFAULT_SANDBOX_TIMEOUT,
    working_dir: str | None = None,
    env: Mapping[str, str] | None = None,
    authority: Authority = 'operator',
    path_authority: Mapping[str, Authority] | None = None,
) -> E2BSandbox[Any]
```

Build from an agent spec, naming the fields a spec can express.

Core reads this signature to generate the spec’s JSON schema. Inherited, core falls back to the variadic base `from_spec`, because `client`’s `e2b.E2B` hint is a `TYPE_CHECKING` import, and publishes only the bare `'E2BSandbox'`.

###### Returns

`E2BSandbox`\[[`Any`](https://docs.python.org/3/library/typing.html#typing.Any)\]

##### backend

```python
def backend(ref: WorkspaceRef) -> E2BSandboxBackend
```

Attach lazily to an existing E2B sandbox.

###### Returns

`E2BSandboxBackend`

##### destroy

`@async`

```python
def destroy(ref: WorkspaceRef) -> None
```

Kill a sandbox by ID, including paused sandboxes, without attaching.

###### Returns

[`None`](https://docs.python.org/3/builtins/constants.html#None)

##### get\_workspace

```python
def get_workspace(
    ctx: RunContext[AgentDepsT],
    *,
    ref: WorkspaceRef | None,
) -> WorkspaceBackend | None
```

The backend for this run, in an `AuthorityWorkspace` when `authority` or `path_authority` asks for one.

###### Returns

`WorkspaceBackend` | [`None`](https://docs.python.org/3/builtins/constants.html#None)

### E2BSandboxBackend

**Bases:** `WorkspaceBackend`, `SupportsCommands`, `SupportsFilesystem`

An [E2B](https://e2b.dev/) sandbox as a Pydantic AI [`WorkspaceBackend`](https://pydantic.dev/docs/ai/api/pydantic-ai/workspaces/#pydantic_ai.workspaces.WorkspaceBackend).

Commands and file operations run inside an E2B microVM, not on the host.

Building one does no I/O. The first operation creates or attaches to a workspace, and the typed `e2b.AsyncSandbox` is available through `get_sandbox()`. The backend does not kill the sandbox; killing it is the application’s job.

Commands run as one-shot operations, with complete output returned after they finish.

Every command runs through `/bin/bash -l -c`, so an argv sequence is quoted into a single shell word string first and login startup files run before the command does; a `shell=True` string runs under `/bin/sh -c` inside that login shell. E2B’s own command `timeout` abandons the output stream and leaves the command running, so the deadline is enforced client-side instead. On timeout or cancellation (including while starting), a separate command signals the process group when `setsid` is available. Custom templates without `setsid` fall back to stopping the command leader only.

The E2B SDK runs every request on asyncio, so under Trio every operation raises `UserError` before it reaches E2B.

#### Constructor Parameters

**`sandbox`**: `e2b.AsyncSandbox` | [`None`](https://docs.python.org/3/builtins/constants.html#None) *Default:* `None`

A live `e2b.AsyncSandbox` you already have. Whoever created it owns killing it.

**`client`**: `e2b.E2B` | [`None`](https://docs.python.org/3/builtins/constants.html#None) *Default:* `None`

An `e2b.E2B` to create or attach with, for its API key and other connection settings; `E2B_API_KEY` and the rest of the environment when `None`.

**`ref`**: `WorkspaceRef` | [`None`](https://docs.python.org/3/builtins/constants.html#None) *Default:* `None`

Identity of an existing sandbox to attach to on first use.

**`template`**: [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) *Default:* `None`

E2B template name or ID a newly created sandbox runs; E2B’s default when `None`. An unknown template raises `WorkspaceUnavailableError` on first use. Custom templates need `/bin/bash` and `/bin/sh`; without `setsid`, stop targets only the leader.

**`allow_internet_access`**: [`bool`](https://docs.python.org/3/builtins/functions.html#bool) *Default:* `True`

Whether a newly created sandbox may reach the internet.

**`sandbox_timeout`**: [`int`](https://docs.python.org/3/builtins/functions.html#int) *Default:* `DEFAULT_SANDBOX_TIMEOUT`

Total lifetime of the sandbox in seconds, applied when it is created and again when attaching to it. When it runs out, E2B pauses the sandbox rather than killing it, and attaching resumes it. The default, 3600, is the most E2B’s Hobby plan allows; Pro plans allow up to 86400.

**`working_dir`**: [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) *Default:* `None`

Absolute directory commands start in and relative paths resolve against. E2B has no create-time working directory, so this is applied per command, including on an attached sandbox; `None` uses the sandbox’s own default, discovered with `pwd -P` on first use.

**`env`**: [`Mapping`](https://docs.python.org/3/library/typing.html#typing.Mapping) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)\] | [`None`](https://docs.python.org/3/builtins/constants.html#None) *Default:* `None`

Environment variables every command gets, on a created or an attached sandbox; per-command `env` is layered on top. Nothing is read from the host environment.

**`network`**: `SandboxNetworkOpts` | [`None`](https://docs.python.org/3/builtins/constants.html#None) *Default:* `None`

E2B’s network options for a newly created sandbox, passed to `Sandbox.create` unchanged: egress allow and deny lists, and `rules` that set headers on requests to a host, from E2B’s proxy outside the sandbox. An attached sandbox keeps the options it was created with.

#### Attributes

##### ref

Identity of the sandbox, or `None` before one has been created.

**Type:** `WorkspaceRef` | [`None`](https://docs.python.org/3/builtins/constants.html#None)

#### Methods

##### get\_sandbox

`@async`

```python
def get_sandbox() -> e2b.AsyncSandbox
```

Return the typed `e2b.AsyncSandbox`, for E2B features the workspace API does not cover.

On a backend with no sandbox yet, this creates one (which E2B bills) or attaches to the one `ref` names, just like the first operation; attaching resumes a paused sandbox. Attaching by `ref` to a sandbox that no longer exists raises `WorkspaceUnavailableError`; it does not create a replacement. After that it returns the cached handle without checking that the sandbox is still running: one killed elsewhere surfaces on the next operation. Calling this does not make you responsible for killing the sandbox; whoever holds the `ref` decides, as before.

###### Returns

`e2b.AsyncSandbox`

##### working\_dir

`@async`

```python
def working_dir() -> str
```

The canonical absolute directory commands start in.

###### Returns

[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### run

`@async`

```python
def run(
    command: WorkspaceCommand,
    *,
    shell: bool = False,
    env: Mapping[str, str] | None = None,
    timeout: float | None = None,
) -> CommandResult
```

Run a command, killing it on timeout, cancellation, or a failed result read.

###### Returns

`CommandResult`
