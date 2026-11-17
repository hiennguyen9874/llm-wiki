---
title: "Pydantic AI + E2B: sandboxed coding agents in Python"
author: "Laís Carvalho"
site: "Pydantic"
published: 2026-10-22T09:00:00.000Z
source: "https://pydantic.dev/articles/pydantic-ai-e2b-sandboxes"
domain: "pydantic.dev"
language: "en"
description: "Run Pydantic AI agents in E2B cloud sandboxes with the native E2BSandbox capability. Pause and resume between runs, and recover a Temporal worker crash."
word_count: 2127
---

A coding agent that can run `python -m unittest` and edit files is useful. A coding agent that runs them on your laptop, as you, with your SSH keys in `~/.ssh` and your production `.env` two directories up, is a liability you have agreed to without reading the terms and conditions. The agent decided what to run, and nobody reviewed the command before it ran. An agent that waited for review would not be an agent.

[E2B](https://e2b.dev/) is now a native sandbox provider in [Pydantic AI](https://pydantic.dev/docs/ai/). Add `E2BSandbox()` to an agent's capabilities and every shell command and file operation the agent makes runs inside an isolated E2B microVM instead of on your machine. Nothing from your environment reaches the sandbox. The sandbox can pause when a run ends and resume when the next one starts, with its filesystem and memory intact. And because the workspace is identified by a credential-free reference, a durable workflow can carry it across a worker crash.

This post walks through two examples from the [E2B cookbook](https://github.com/e2b-dev/e2b-cookbook): a two-run diagnose-then-fix agent that pauses the sandbox between runs, and the same task inside a Temporal workflow where the worker process gets killed halfway through.

## One line, and the agent is off your machine

Install the harness with the E2B and Temporal extras, the provider extras the snippets below use (the quick start calls Anthropic, the cookbook examples call OpenAI), and the [Logfire](https://pydantic.dev/logfire) extra so the runs are traced. Then set `E2B_API_KEY` and the provider key:

```bash
uv add "pydantic-ai-harness[e2b,anthropic,temporal]" "pydantic-ai-slim[openai,logfire]"
```

Then give the agent the sandbox alongside the tools that will use it:

```python
import logfire
from pydantic_ai import Agent
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.e2b_sandbox import E2BSandbox

logfire.configure()
logfire.instrument_pydantic_ai()

agent = Agent('anthropic:claude-opus-5-5', capabilities=[E2BSandbox(), Coder()])
result = agent.run_sync('Clone https://github.com/pydantic/pydantic-ai and summarize how capabilities work.')
```

`E2BSandbox` supplies execution only. `Coder`, or the narrower `Shell` and `FileSystem` capabilities, supply the tools, and those tools now run in the sandbox. There is no custom E2B adapter and no template to build. E2B's default template ships with Python and git, which is enough for this post; a project with its own dependencies installs them in a [custom template](https://pydantic.dev/docs/ai/harness/e2b-sandbox/) or with a `pip install` run inside the sandbox before the agent starts, since the default template has pip but not uv.

A few defaults worth knowing before the first run. A sandbox lives for an hour unless you pass `sandbox_timeout`, and when that runs out E2B pauses it rather than killing it. Internet access is on unless you turn it off with `allow_internet_access=False`. And Pydantic AI never kills a sandbox when a run ends: the application that created it owns its lifetime, and a sandbox you forget is a sandbox you are paying for. The [E2B sandbox guide](https://pydantic.dev/docs/ai/harness/e2b-sandbox/) covers cleanup, including an `on_run_error` hook for runs that fail before there is a result to read a reference from.

## Diagnose, pause, resume, fix

The [first cookbook example](https://github.com/e2b-dev/e2b-cookbook/tree/main/examples/pydantic-ai-python) gives the agent a small Python CLI that summarizes JSONL API request logs. Its tests fail: the CLI counts server errors wrong and computes p95 latency wrong. The agent gets two runs. The first reads the code and the failing tests and writes `diagnosis.md` without touching the source. The application then pauses the sandbox, builds a fresh backend attached to it, and a second run fixes the bug using the saved diagnosis and the first run's conversation history.

The agent definition is ordinary Pydantic AI. The only E2B-specific part is the capability:

```python
import logfire
from pydantic_ai import Agent
from pydantic_ai_harness.e2b_sandbox import E2BSandbox
from pydantic_ai_harness.filesystem import FileSystem
from pydantic_ai_harness.shell import Shell

logfire.configure()
logfire.instrument_pydantic_ai()

WORKDIR = '/home/user/log-cli'

agent = Agent(
    'openai:gpt-4.1-mini',
    name='log_cli_fixer',
    instructions='Work only in this sandbox project. Use the supplied tools; verify claims by running tests.',
    capabilities=[
        E2BSandbox(
            working_dir=WORKDIR,
            sandbox_timeout=600,
            allow_internet_access=False,
        ),
        Shell(tools=['run_command'], default_timeout=20, max_output_chars=6000),
        FileSystem(tools=['read_file', 'write_file', 'edit_file']),
    ],
)
```

The cookbook narrows the tool surface on purpose. `Shell` exposes only `run_command`, `FileSystem` exposes three file tools, and internet access is off because the fixture needs no downloads. A sandbox is a boundary, and a narrow tool list makes the boundary cheaper to reason about.

The application seeds the fixture before the agent starts, by constructing the backend itself and working in it through `Workspace`:

```python
from pydantic_ai.workspaces import Workspace
from pydantic_ai_harness.e2b_sandbox import E2BSandbox, E2BSandboxBackend

backend = E2BSandboxBackend(working_dir=WORKDIR, sandbox_timeout=600, allow_internet_access=False)
workspace = Workspace(backend)
for name in ('log_stats.py', 'test_log_stats.py', 'requests.jsonl'):
    await workspace.write_bytes(name, (FIXTURE / name).read_bytes())

first = await agent.run(DIAGNOSE, workspace=backend, usage_limits=limits())
ref = first.workspace.ref
```

Building the backend does no I/O. The first `write_bytes` creates the sandbox, and from then on `backend.ref` identifies it. The run result carries the same reference in `first.workspace.ref`.

Now the pause. The application asks the backend for the typed `e2b.AsyncSandbox`, pauses it, and then constructs a new backend that knows only the reference:

```python
sandbox = await backend.get_sandbox()
assert await sandbox.pause()

attached = E2BSandbox(working_dir=WORKDIR, sandbox_timeout=600).backend(ref)
continued = Workspace(attached)
assert (await continued.read_text('diagnosis.md')).strip()

second = await agent.run(
    FIX,
    workspace=ref,
    message_history=first.all_messages(),
    usage_limits=limits(),
)
assert second.workspace.ref == ref
```

The attached backend's first file read resumes the paused sandbox. [E2B keeps a paused sandbox indefinitely](https://e2b.dev/docs/sandbox/persistence), filesystem and memory both, so `diagnosis.md` is where the first run left it. The second run gets `workspace=ref` to select the sandbox and `message_history` to carry the conversation. Either the ref or a history that names it will select the sandbox, but only the history carries what the agent already knows, and the cookbook passes both.

The example then does something I want more agent demos to do: it checks the agent's work instead of trusting the agent's summary. It restores the test file from the trusted host fixture, because a shell command can bypass a file tool's restrictions, confirms the input logs were not edited, and runs the tests itself. Four tests pass, the CLI prints the right counts, and the application kills the sandbox in a `finally` block and confirms it is gone from the account.

```
Created sandbox: <id>
Diagnosis saved. Model usage: ...
Paused sandbox: <id>
Resumed sandbox: <same id>; checksums unchanged before repair
...
Ran 4 tests ...
OK
CLI: {"requests": 4, "server_errors": 2, "p95_ms": 100}
Cleanup verified: <same id>
```

The script asserts sandbox identity and SHA-256 checksums before and after the pause. The same id, the same bytes.

## Kill the worker, keep the sandbox

The pause-and-resume example proves the sandbox outlives a run. The [Temporal example](https://github.com/e2b-dev/e2b-cookbook/tree/main/examples/pydantic-ai-temporal-python) proves it outlives the process that was driving the agent.

The task is the same log CLI. This time the two agent runs live inside a Temporal workflow, and between them the demo sends `SIGKILL` to the worker. No Python `finally`, no graceful shutdown. A new worker starts on the same task queue, Temporal replays the recorded history, and the workflow continues the repair in the sandbox the dead worker left behind.

`TemporalDurability` joins the capability list and the agent is otherwise the one from the first example. The cookbook builds it in a shared `make_agent()` helper; written out in full, with the Temporal activity settings the example uses, it is:

```python
from datetime import timedelta

import logfire
from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import TemporalDurability
from pydantic_ai_harness.e2b_sandbox import E2BSandbox
from pydantic_ai_harness.filesystem import FileSystem
from pydantic_ai_harness.shell import Shell
from temporalio.common import RetryPolicy

logfire.configure()
logfire.instrument_pydantic_ai()

WORKDIR = '/home/user/log-cli'

agent = Agent(
    'openai:gpt-4.1-mini',
    name='log_cli_fixer',
    instructions='Work only in this sandbox project. Use the supplied tools; verify claims by running tests.',
    capabilities=[
        E2BSandbox(working_dir=WORKDIR, sandbox_timeout=600, allow_internet_access=False),
        Shell(tools=['run_command'], default_timeout=20, max_output_chars=6000),
        FileSystem(tools=['read_file', 'write_file', 'edit_file']),
        TemporalDurability(
            activity_config={
                'start_to_close_timeout': timedelta(seconds=45),
                'retry_policy': RetryPolicy(maximum_attempts=2),
            },
        ),
    ],
)
```

The agent needs a `name`, and both it and the workflow must be defined at module level so Temporal can register the activities. Both worker processes import the same module.

The workflow takes the sandbox reference as its input. That matters: the controller creates and seeds one sandbox, then hands the workflow a `WorkspaceRef`, which holds no credentials. Temporal records that input before any worker touches the agent, so whichever worker ends up running the second half of the job knows which sandbox to attach to.

This is the cookbook's `workflow.py`, trimmed to the parts that matter. `DIAGNOSE`, `FIX`, `fingerprints`, and `limits` are the prompts, the checksum helper, and the `UsageLimits` from the example's `project.py`:

```python
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from agent import agent
    from project import DIAGNOSE, FIX, fingerprints, limits
    from pydantic_ai.durable_exec.temporal import PydanticAIWorkflow
    from pydantic_ai.workspaces import WorkspaceRef

@workflow.defn
class FixLogCLI(PydanticAIWorkflow):
    __pydantic_ai_agents__ = (agent,)

    def __init__(self):
        self.checkpoint = None
        self.proceed = False

    @workflow.query
    def diagnosis_checkpoint(self) -> dict | None:
        return self.checkpoint

    @workflow.signal
    def continue_fix(self) -> None:
        self.proceed = True

    @workflow.run
    async def run(self, ref: WorkspaceRef) -> dict:
        first = await agent.run(DIAGNOSE, workspace=ref, usage_limits=limits())
        saved = await fingerprints(first.workspace)
        self.checkpoint = {'sandbox_id': ref.id, 'checksums': saved}

        await workflow.wait_condition(lambda: self.proceed, timeout=180)
        assert await fingerprints(first.workspace) == saved
        second = await agent.run(
            FIX,
            workspace=ref,
            message_history=first.all_messages(),
            usage_limits=limits(),
        )
        return {'sandbox_id': ref.id, 'summary': second.output}
```

The `wait_condition` between diagnosis and repair gives the crash a repeatable place to happen. The controller polls the `diagnosis_checkpoint` query until the first run has saved its diagnosis, kills the worker, starts another, polls the same query again, and only then sends `continue_fix`. The recovered checkpoint matches the one the dead worker recorded.

```
Created sandbox: <id>
Worker started: pid=<first pid>
Durable checkpoint: <id>; diagnosis and files saved
Worker crashed: pid=<first pid>, exit=-9
Worker started: pid=<different pid>
Checkpoint recovered by pid=<different pid>; sandbox=<same id>
...
Ran 4 tests ...
OK
Exactly one sandbox; original workflow completed after worker restart
Cleanup verified: <same id>
```

The final resource check is the line I would read first. Exactly one new sandbox exists in the account after the whole sequence, running or paused. A naive recovery would have created a second one and started the job over in an empty directory. `E2BSandbox` raises `WorkspaceUnavailableError` when a reference points at a sandbox that no longer exists, rather than quietly provisioning a replacement. Recovery either continues where the diagnosis left off or fails loudly.

The cookbook README is careful about what this does and does not prove, and the care is worth repeating. The crash happens at an idle checkpoint, with no command in flight. Temporal activities can run again if a worker disappears before completion is recorded, so shell commands are at-least-once, not exactly-once. Recovery does not roll back file writes. Write tools that replace a named result rather than appending to one, and you get the same answer however many times the activity runs.

## Where the trace goes

`E2BSandbox` emits no spans of its own. Pydantic AI's instrumentation records the sandbox on the agent run span as `pydantic_ai.workspace.provider` and `pydantic_ai.workspace.id`, and every command or file operation a tool makes runs inside that tool call's span. With the two `logfire` lines from the snippets above in place, [Pydantic Logfire](https://pydantic.dev/logfire) shows the diagnosis run and the resumed run, each `run_command` inside them, and the same sandbox id on both, so a trace matches up with the E2B dashboard. In the Temporal example the two runs sit under the same workflow, so the crash reads as a gap between two activities rather than as two unrelated jobs.

If you are not sending traces yet, [Pydantic Logfire](https://pydantic.dev/logfire) has a Personal plan with 10 million telemetry records a month and a $0 hard cap, which is plenty for both cookbook examples. Create a project, run `logfire auth` once, and the two lines in the snippets above do the rest: every model request, every `run_command`, and the sandbox id that ties a run to the E2B dashboard, in one trace you can query with SQL.

## Get started

Both cookbook examples run from a checkout with `uv sync --locked` and two environment variables, `E2B_API_KEY` and a model provider key. Each agent run is bounded to eight model requests and a $0.10 estimated-cost limit through `UsageLimits`, so a mistake in the prompt is cheap to find. The cost estimate depends on provider pricing data, the final request can exceed it, and neither limit is an account spending cap. The Temporal example starts its own local dev server and needs no Docker.

- New to [Pydantic AI](https://pydantic.dev/docs/ai/)? The quick start takes about five minutes, and `E2BSandbox` is one capability in the list once you have an agent that runs. The install command at the top of this post covers every example here, including the Temporal one.
- [E2B sandbox guide](https://pydantic.dev/docs/ai/harness/e2b-sandbox/) in the Pydantic AI docs, including configuration, cleanup hooks, and the dev-server preview pattern.
- [Pause and resume example](https://github.com/e2b-dev/e2b-cookbook/tree/main/examples/pydantic-ai-python) in the E2B cookbook.
- [Temporal crash-recovery example](https://github.com/e2b-dev/e2b-cookbook/tree/main/examples/pydantic-ai-temporal-python) in the E2B cookbook.
- [Durable execution with Temporal](https://pydantic.dev/docs/ai/capabilities/durable_execution/temporal/) in the Pydantic AI docs.
- [E2B sandbox persistence](https://e2b.dev/docs/sandbox/persistence) for what pause and resume preserve, and for how long.

The agent still runs `python -m unittest` and edits files. It just does it somewhere that is not your laptop, and picks up where it left off when you ask it to.
