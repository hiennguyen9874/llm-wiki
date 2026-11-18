---
title: "Deferred Tools"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/"
domain: "pydantic.dev"
language: "en"
description: "Add human-in-the-loop tool approval to Pydantic AI agents, or hand tool calls to a frontend or background worker, and resume the run with the results."
word_count: 3310
---

There are a few scenarios where the model should be able to call a tool that should not or cannot be executed during the same agent run inside the same Python process:

- it may need to be approved by the user first
- it may depend on an upstream service, frontend, or user to provide the result
- the result could take longer to generate than it’s reasonable to keep the agent process running

To support these use cases, Pydantic AI provides the concept of deferred tools, which come in two flavors documented below:

- tools that [require approval](#human-in-the-loop-tool-approval)
- tools that are [executed externally](#external-tool-execution)

When the model calls a deferred tool, there are two ways to resolve it:

- **Resolve it inline**, using a [`HandleDeferredToolCalls`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.HandleDeferredToolCalls) [capability](https://pydantic.dev/docs/ai/capabilities/overview/) with a handler that resolves some or all of the pending calls. The agent run continues in a single call without needing to end and restart — use this when the resolver (e.g. an approval gate, an external service client) lives in the same process as the agent. See [Resolving deferred calls with a handler](#resolving-deferred-calls-with-a-handler).
- **End the run** with a [`DeferredToolRequests`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolRequests) output object containing information about the deferred tool calls; the caller gathers approvals/results and then starts a new agent run with the original run’s [message history](https://pydantic.dev/docs/ai/core-concepts/message-history/) plus a [`DeferredToolResults`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolResults) object. That follow-up is a separate agent run with its own [`run_id`](https://pydantic.dev/docs/ai/core-concepts/message-history/#correlating-runs-with-run_id-and-conversation_id) (do not reuse the paused run’s); keep pause/resume correlation via `conversation_id`. Use this when the resolver lives outside the agent process — e.g. a UI adapter that surfaces pending calls to a user and starts a follow-up run once it has their response.

The two flows compose: a handler can resolve a subset of calls and let the rest bubble up as `DeferredToolRequests` output for an outer caller to handle.

To wait for an answer from outside the process without ending the run, give the [`HandleDeferredToolCalls`](https://pydantic.dev/docs/ai/capabilities/handle-deferred-tool-calls/#two-forms-of-handler) handler a third parameter, a resume token. It either answers right away or hands the token to the approver, and your approval endpoint resolves the token with the decision. By default the wait happens in your process. In a [durable execution](https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/) run on an engine that supports it, currently [AWS Lambda durable functions](https://pydantic.dev/docs/ai/harness/aws-lambda/#approvals), the engine records the wait and suspends the run until the decision arrives.

Each pending call says what it waits for: [`DeferredToolRequests.kind()`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolRequests.kind) returns `'approval'` for a call in `approvals`, and `'question'` or `'external'` for one in `calls`. A tool marks a call as a question for the user, rather than work done elsewhere, with `raise CallDeferred(kind='question')`; Pydantic AI Harness’s [`AskUser`](https://pydantic.dev/docs/ai/harness/ask-user/) does. The answer can say who gave it in [`DeferredToolResults.answered_by`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolResults.answered_by), which Pydantic AI reports but doesn’t check.

The stop-the-world flow requires `DeferredToolRequests` to be in the `Agent`’s [`output_type`](https://pydantic.dev/docs/ai/core-concepts/output/#structured-output) so that the possible types of the agent run output are correctly inferred. If your agent can also be used in a context where no deferred tools are available and you don’t want to deal with that type everywhere you use the agent, you can instead pass the `output_type` argument when you run the agent using [`agent.run()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run), [`agent.run_sync()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_sync), [`agent.run_stream()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_stream), or [`agent.iter()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.iter). Note that the run-time `output_type` overrides the one specified at construction time (for type inference reasons), so you’ll need to include the original output type explicitly.

## Resolving deferred calls with a handler

The recommended way to handle deferred tool calls is to register a [`HandleDeferredToolCalls`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.HandleDeferredToolCalls) [capability](https://pydantic.dev/docs/ai/capabilities/overview/) whose handler receives the [`DeferredToolRequests`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolRequests) and returns a [`DeferredToolResults`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolResults) resolving some or all of them. The tool execution pipeline applies the results inline and the agent run continues in a single call, as if the deferred tools had returned normally.

With a handler in place, `DeferredToolRequests` no longer needs to be declared as an output type — unless you also want unresolved calls to bubble up to the caller (see below).

[`DeferredToolRequests.build_results()`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolRequests.build_results) is a convenience constructor — it validates that every tool call ID refers to a pending request of the correct kind, and accepts `approve_all=True` to auto-approve any approval requests not otherwise specified.

deferred\_tool\_handler.py

```python
from pydantic_ai import (
    Agent,
    ApprovalRequired,
    CallDeferred,
    DeferredToolRequests,
    DeferredToolResults,
    RunContext,
    ToolDenied,
)
from pydantic_ai.capabilities import HandleDeferredToolCalls

async def handle_deferred(
    ctx: RunContext, requests: DeferredToolRequests
) -> DeferredToolResults:
    approvals: dict[str, bool | ToolDenied] = {}
    for call in requests.approvals:
        if call.tool_name == 'delete_file':
            approvals[call.tool_call_id] = ToolDenied('Deleting files is not allowed')
        else:
            approvals[call.tool_call_id] = True

    calls = {call.tool_call_id: f'(external result for {call.tool_name})' for call in requests.calls}

    return requests.build_results(approvals=approvals, calls=calls)

agent = Agent(
    'openai:gpt-6.1-sol',
    capabilities=[HandleDeferredToolCalls(handler=handle_deferred)],
)

@agent.tool_plain(requires_approval=True)
def delete_file(path: str) -> str:
    return f'File {path!r} deleted'  # (1)

@agent.tool
def update_file(ctx: RunContext, path: str, content: str) -> str:
    if path == '.env' and not ctx.tool_call_approved:
        raise ApprovalRequired
    return f'File {path!r} updated: {content!r}'

@agent.tool_plain
async def send_to_worker(task: str) -> str:
    raise CallDeferred  # (2)
```

Never reached here — the handler denies this call, so the model sees the denial message instead.

The handler supplies the result for this external call, so the tool body just signals the deferral.

If the handler declines to resolve some or all of the calls (by omitting them from the returned [`DeferredToolResults`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolResults) or returning `None`), the next [`HandleDeferredToolCalls`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.HandleDeferredToolCalls) (or any other capability that overrides the [`handle_deferred_tool_calls`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.AbstractCapability.handle_deferred_tool_calls) hook) gets a chance, and any still-unresolved calls bubble up as a [`DeferredToolRequests`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolRequests) output. To allow that bubble-up, include `DeferredToolRequests` in the agent’s `output_type` — so you can combine inline handling with the stop-the-world flow when it makes sense.

If you’re [building a custom capability](https://pydantic.dev/docs/ai/capabilities/custom/) that needs to resolve approvals or external calls itself (e.g. a sandbox that exposes deferred tools), override the [`handle_deferred_tool_calls`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.AbstractCapability.handle_deferred_tool_calls) hook directly on your capability instead of registering a separate `HandleDeferredToolCalls`. The same hook is also available via the [`Hooks`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.Hooks) capability — see [Hooks](https://pydantic.dev/docs/ai/core-concepts/hooks/#deferred-tool-call-hook).

The sections below describe the two kinds of deferred tools the handler can resolve, as well as the alternative stop-the-world flow for each. See [Capabilities](https://pydantic.dev/docs/ai/capabilities/overview/) for how multiple capabilities compose, including [`WrapperCapability`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.WrapperCapability) and the `capabilities=[...]` list.

## Human-in-the-Loop Tool Approval

If a tool function always requires approval, you can pass the `requires_approval=True` argument to the [`@agent.tool`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.tool) decorator, [`@agent.tool_plain`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.tool_plain) decorator, [`Tool`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.Tool) class, [`FunctionToolset.tool`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.FunctionToolset.tool) decorator, or [`FunctionToolset.add_function()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.FunctionToolset.add_function) method. Inside the function, you can then assume that the tool call has been approved.

To require approval for every tool in a [`FunctionToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.FunctionToolset), pass `requires_approval=True` to its constructor. It applies to `Tool` instances too; only a function added with `requires_approval=False` opts out.

In a [realtime session](https://pydantic.dev/docs/ai/realtime/tools/#deferred-and-approval-required-tools), approval must be resolved inline, typically by a [`HandleDeferredToolCalls`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.HandleDeferredToolCalls) handler (a capability hook can resolve it too); a call nothing resolves is refused every time.

If approval depends on the tool call’s arguments or the agent [run context](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext), such as [dependencies](https://pydantic.dev/docs/ai/core-concepts/dependencies/) or message history, raise [`ApprovalRequired`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ApprovalRequired) from the tool function. The [`RunContext.tool_call_approved`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.tool_call_approved) property will be `True` if the tool call has already been approved.

You can also raise it from the tool’s [`args_validator`](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#args-validator), which runs before the tool function and lets you reject invalid arguments before asking a human to approve them.

To require approval for calls to tools provided by a [toolset](https://pydantic.dev/docs/ai/tools-toolsets/toolsets/) (like an [MCP server](https://pydantic.dev/docs/ai/mcp/client/)), see the [`ApprovalRequiredToolset` documentation](https://pydantic.dev/docs/ai/tools-toolsets/toolsets/#requiring-tool-approval).

When the model calls a tool that requires approval, the agent run will end with a [`DeferredToolRequests`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolRequests) output object with an `approvals` list holding [`ToolCallPart`s](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ToolCallPart) containing the tool name, the arguments as the model sent them, and a unique tool call ID.

If a capability’s [tool validation hook](https://pydantic.dev/docs/ai/core-concepts/hooks/#tool-validation-hooks), such as `after_tool_validate`, rewrites a tool’s arguments, the approval request still shows the model’s arguments, but the tool runs with the rewritten ones: validation, hooks included, runs again when the approved call resumes. To make the change after approval instead, rewrite the arguments in [`before_tool_execute`](https://pydantic.dev/docs/ai/core-concepts/hooks/#tool-execution-hooks), which for a `requires_approval=True` tool runs only once the call is approved. To let whoever approves the call change its arguments, approve it with [`ToolApproved(override_args=...)`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.ToolApproved); validation, hooks included, then runs on those arguments instead of the model’s.

Once you’ve gathered the user’s approvals or denials, you can build a [`DeferredToolResults`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolResults) object with an `approvals` dictionary that maps each tool call ID to a boolean, a [`ToolApproved`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.ToolApproved) object (with optional `override_args`), or a [`ToolDenied`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.ToolDenied) object (with an optional custom `message` to provide to the model). You can also provide a `metadata` dictionary on `DeferredToolResults` that maps each tool call ID to a dictionary of metadata that will be available in the tool’s [`RunContext.tool_call_metadata`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.tool_call_metadata) attribute. This `DeferredToolResults` object can then be provided to one of the agent run methods as `deferred_tool_results`, alongside the original run’s [message history](https://pydantic.dev/docs/ai/core-concepts/message-history/) or its [conversation](#pausing-a-conversation), which also keeps the requests for when the answers come later.

Here’s an example that shows how to require approval for all file deletions, and for updates of specific protected files:

tool\_requires\_approval.py

```python
from pydantic_ai import (
    Agent,
    ApprovalRequired,
    DeferredToolRequests,
    DeferredToolResults,
    RunContext,
    ToolDenied,
)

agent = Agent('openai:gpt-6.1-sol', output_type=[str, DeferredToolRequests])

PROTECTED_FILES = {'.env'}

@agent.tool
def update_file(ctx: RunContext, path: str, content: str) -> str:
    if path in PROTECTED_FILES and not ctx.tool_call_approved:
        raise ApprovalRequired(metadata={'reason': 'protected'})  # (1)
    return f'File {path!r} updated: {content!r}'

@agent.tool_plain(requires_approval=True)
def delete_file(path: str) -> str:
    return f'File {path!r} deleted'

result = agent.run_sync('Delete `__init__.py`, write `Hello, world!` to `README.md`, and clear `.env`')
messages = result.all_messages()

assert isinstance(result.output, DeferredToolRequests)
requests = result.output
print(requests)
"""
DeferredToolRequests(
    calls=[],
    approvals=[
        ToolCallPart(
            tool_name='update_file',
            args={'path': '.env', 'content': ''},
            tool_call_id='update_file_dotenv',
        ),
        ToolCallPart(
            tool_name='delete_file',
            args={'path': '__init__.py'},
            tool_call_id='delete_file',
        ),
    ],
    metadata={'update_file_dotenv': {'reason': 'protected'}},
)
"""

results = DeferredToolResults()
for call in requests.approvals:
    result = False
    if call.tool_name == 'update_file':
        # Approve all updates
        result = True
    elif call.tool_name == 'delete_file':
        # deny all deletes
        result = ToolDenied('Deleting files is not allowed')

    results.approvals[call.tool_call_id] = result

result = agent.run_sync(
    'Now create a backup of README.md',  # (2)
    message_history=messages,
    deferred_tool_results=results,
)
print(result.output)
"""
Here's what I've done:
- Attempted to delete __init__.py, but deletion is not allowed.
- Updated README.md with: Hello, world!
- Cleared .env (set to empty).
- Created a backup at README.md.bak containing: Hello, world!

If you want a different backup name or format (e.g., timestamped like README_2025-11-24.bak), let me know.
"""
print(result.all_messages())
"""
[
    ModelRequest(
        parts=[
            UserPromptPart(
                content='Delete `__init__.py`, write `Hello, world!` to `README.md`, and clear `.env`',
                timestamp=datetime.datetime(...),
            )
        ],
        timestamp=datetime.datetime(...),
        run_id='...',
        conversation_id='...',
    ),
    ModelResponse(
        parts=[
            ToolCallPart(
                tool_name='delete_file',
                args={'path': '__init__.py'},
                tool_call_id='delete_file',
            ),
            ToolCallPart(
                tool_name='update_file',
                args={'path': 'README.md', 'content': 'Hello, world!'},
                tool_call_id='update_file_readme',
            ),
            ToolCallPart(
                tool_name='update_file',
                args={'path': '.env', 'content': ''},
                tool_call_id='update_file_dotenv',
            ),
        ],
        usage=RequestUsage(cost=Decimal('0.000336'), input_tokens=63, output_tokens=21),
        model_name='gpt-6.1-sol',
        model_id='openai:gpt-6.1-sol',
        timestamp=datetime.datetime(...),
        run_id='...',
        conversation_id='...',
    ),
    ModelRequest(
        parts=[
            ToolReturnPart(
                tool_name='update_file',
                content="File 'README.md' updated: 'Hello, world!'",
                tool_call_id='update_file_readme',
                timestamp=datetime.datetime(...),
            )
        ],
        timestamp=datetime.datetime(...),
        run_id='...',
        conversation_id='...',
    ),
    ModelRequest(
        parts=[
            ToolReturnPart(
                tool_name='delete_file',
                content='Deleting files is not allowed',
                tool_call_id='delete_file',
                timestamp=datetime.datetime(...),
                outcome='denied',
            ),
            ToolReturnPart(
                tool_name='update_file',
                content="File '.env' updated: ''",
                tool_call_id='update_file_dotenv',
                timestamp=datetime.datetime(...),
            ),
            UserPromptPart(
                content='Now create a backup of README.md',
                timestamp=datetime.datetime(...),
            ),
        ],
        timestamp=datetime.datetime(...),
        run_id='...',
        conversation_id='...',
    ),
    ModelResponse(
        parts=[
            ToolCallPart(
                tool_name='update_file',
                args={'path': 'README.md.bak', 'content': 'Hello, world!'},
                tool_call_id='update_file_backup',
            )
        ],
        usage=RequestUsage(cost=Decimal('0.000482'), input_tokens=86, output_tokens=31),
        model_name='gpt-6.1-sol',
        model_id='openai:gpt-6.1-sol',
        timestamp=datetime.datetime(...),
        run_id='...',
        conversation_id='...',
    ),
    ModelRequest(
        parts=[
            ToolReturnPart(
                tool_name='update_file',
                content="File 'README.md.bak' updated: 'Hello, world!'",
                tool_call_id='update_file_backup',
                timestamp=datetime.datetime(...),
            )
        ],
        timestamp=datetime.datetime(...),
        run_id='...',
        conversation_id='...',
    ),
    ModelResponse(
        parts=[
            TextPart(
                content="Here's what I've done:\n- Attempted to delete __init__.py, but deletion is not allowed.\n- Updated README.md with: Hello, world!\n- Cleared .env (set to empty).\n- Created a backup at README.md.bak containing: Hello, world!\n\nIf you want a different backup name or format (e.g., timestamped like README_2025-11-24.bak), let me know."
            )
        ],
        usage=RequestUsage(cost=Decimal('0.001076'), input_tokens=93, output_tokens=89),
        model_name='gpt-6.1-sol',
        model_id='openai:gpt-6.1-sol',
        timestamp=datetime.datetime(...),
        run_id='...',
        conversation_id='...',
    ),
]
"""
```

The optional `metadata` parameter can attach arbitrary context to deferred tool calls, accessible in `DeferredToolRequests.metadata` keyed by `tool_call_id`.

This second agent run continues from where the first run left off, providing the tool approval results and optionally a new `user_prompt` to give the model additional instructions alongside the deferred results.

*(This example is complete, it can be run “as is”)*

## External Tool Execution

When the result of a tool call cannot be generated inside the same agent run in which it was called, the tool is considered to be external. Examples of external tools are client-side tools implemented by a web or app frontend, and slow tasks that are passed off to a background worker or external service instead of keeping the agent process running.

If whether a tool call should be executed externally depends on the tool call arguments, the agent [run context](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext) (e.g. [dependencies](https://pydantic.dev/docs/ai/core-concepts/dependencies/) or message history), or how long the task is expected to take, you can define a tool function and conditionally raise the [`CallDeferred`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.CallDeferred) exception. Before raising the exception, the tool function would typically schedule some background task and pass along the [`RunContext.tool_call_id`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.tool_call_id) so that the result can be matched to the deferred tool call later.

As with approval, the tool’s [`args_validator`](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#args-validator) can raise `CallDeferred` too, so only calls with valid arguments are handed off.

If a tool is always executed externally and its definition is provided to your code along with a JSON schema for its arguments, you can use an [`ExternalToolset`](https://pydantic.dev/docs/ai/tools-toolsets/toolsets/#external-toolset). If the external tools are known up front and you don’t have the arguments JSON schema handy, you can also define a tool function with the appropriate signature that does nothing but raise the [`CallDeferred`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.CallDeferred) exception.

When the model calls an external tool, the agent run will end with a [`DeferredToolRequests`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolRequests) output object with a `calls` list holding [`ToolCallPart`s](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ToolCallPart) containing the tool name, validated arguments, and a unique tool call ID.

Once the tool call results are ready, you can build a [`DeferredToolResults`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolResults) object with a `calls` dictionary that maps each tool call ID to an arbitrary value to be returned to the model, a [`ToolReturn`](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#advanced-tool-returns) object, or an exception in case the tool call failed: a [`ModelRetry`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelRetry) if the model should [try again](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-retries), or a [`ToolFailed`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ToolFailed) if the failure should be reported to the model as a [failed result](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-failed) (without consuming the tool’s retry budget) so it can decide how to proceed. This `DeferredToolResults` object can then be provided to one of the agent run methods as `deferred_tool_results`, alongside the original run’s [message history](https://pydantic.dev/docs/ai/core-concepts/message-history/) or its [conversation](#pausing-a-conversation), which also keeps the requests for when the answers come later.

Here’s an example that shows how to move a task that takes a while to complete to the background and return the result to the model once the task is complete:

external\_tool.py

```python
import asyncio
from dataclasses import dataclass
from typing import Any

from pydantic_ai import (
    Agent,
    CallDeferred,
    DeferredToolRequests,
    DeferredToolResults,
    ModelRetry,
    RunContext,
)

@dataclass
class TaskResult:
    task_id: str
    result: Any

async def calculate_answer_task(task_id: str, question: str) -> TaskResult:
    await asyncio.sleep(1)
    return TaskResult(task_id=task_id, result=42)

agent = Agent('openai:gpt-6.1-sol', output_type=[str, DeferredToolRequests])

tasks: list[asyncio.Task[TaskResult]] = []

@agent.tool
async def calculate_answer(ctx: RunContext, question: str) -> str:
    task_id = f'task_{len(tasks)}'  # (1)
    task = asyncio.create_task(calculate_answer_task(task_id, question))
    tasks.append(task)

    raise CallDeferred(metadata={'task_id': task_id})  # (2)

async def main():
    result = await agent.run('Calculate the answer to the ultimate question of life, the universe, and everything')
    messages = result.all_messages()

    assert isinstance(result.output, DeferredToolRequests)
    requests = result.output
    print(requests)
    """
    DeferredToolRequests(
        calls=[
            ToolCallPart(
                tool_name='calculate_answer',
                args={
                    'question': 'the ultimate question of life, the universe, and everything'
                },
                tool_call_id='pyd_ai_tool_call_id',
            )
        ],
        approvals=[],
        metadata={'pyd_ai_tool_call_id': {'task_id': 'task_0'}},
    )
    """

    done, _ = await asyncio.wait(tasks)  # (3)
    task_results = [task.result() for task in done]
    task_results_by_task_id = {result.task_id: result.result for result in task_results}

    results = DeferredToolResults()
    for call in requests.calls:
        try:
            task_id = requests.metadata[call.tool_call_id]['task_id']
            result = task_results_by_task_id[task_id]
        except KeyError:
            result = ModelRetry('No result for this tool call was found.')

        results.calls[call.tool_call_id] = result

    result = await agent.run(message_history=messages, deferred_tool_results=results)
    print(result.output)
    #> The answer to the ultimate question of life, the universe, and everything is 42.
    print(result.all_messages())
    """
    [
        ModelRequest(
            parts=[
                UserPromptPart(
                    content='Calculate the answer to the ultimate question of life, the universe, and everything',
                    timestamp=datetime.datetime(...),
                )
            ],
            timestamp=datetime.datetime(...),
            run_id='...',
            conversation_id='...',
        ),
        ModelResponse(
            parts=[
                ToolCallPart(
                    tool_name='calculate_answer',
                    args={
                        'question': 'the ultimate question of life, the universe, and everything'
                    },
                    tool_call_id='pyd_ai_tool_call_id',
                )
            ],
            usage=RequestUsage(
                cost=Decimal('0.000256'), input_tokens=63, output_tokens=13
            ),
            model_name='gpt-6.1-sol',
            model_id='openai:gpt-6.1-sol',
            timestamp=datetime.datetime(...),
            run_id='...',
            conversation_id='...',
        ),
        ModelRequest(
            parts=[
                ToolReturnPart(
                    tool_name='calculate_answer',
                    content=42,
                    tool_call_id='pyd_ai_tool_call_id',
                    timestamp=datetime.datetime(...),
                )
            ],
            timestamp=datetime.datetime(...),
            run_id='...',
            conversation_id='...',
        ),
        ModelResponse(
            parts=[
                TextPart(
                    content='The answer to the ultimate question of life, the universe, and everything is 42.'
                )
            ],
            usage=RequestUsage(
                cost=Decimal('0.000408'), input_tokens=64, output_tokens=28
            ),
            model_name='gpt-6.1-sol',
            model_id='openai:gpt-6.1-sol',
            timestamp=datetime.datetime(...),
            run_id='...',
            conversation_id='...',
        ),
    ]
    """
```

Generate a task ID that can be tracked independently of the tool call ID.

The optional `metadata` parameter passes the `task_id` so it can be matched with results later, accessible in `DeferredToolRequests.metadata` keyed by `tool_call_id`.

In reality, this would typically happen in a separate process that polls for the task status or is notified when all pending tasks are complete.

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

## Pausing a conversation

A run that ends with [`DeferredToolRequests`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolRequests) has paused its conversation: the next run can’t go on until the calls are answered, and the answers often come later — a reviewer approves the refund tomorrow, a job finishes on another machine. The run’s [`conversation`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult.conversation) keeps the requests as [`deferred_tool_requests`](https://pydantic.dev/docs/ai/api/pydantic-ai/conversation/#pydantic_ai.conversation.Conversation.deferred_tool_requests), so the conversation you store is everything you need to resume.

That matters because the requests can’t be rebuilt from the messages. The history shows which calls are unanswered, but not which need approval and which an external result, or the metadata a tool attached when it deferred. Store the conversation, and those travel with it:

pausing\_a\_conversation.py

```python
from pydantic_ai import (
    Agent,
    ApprovalRequired,
    ConversationTypeAdapter,
    DeferredToolRequests,
    RunContext,
)

agent = Agent('openai:gpt-6.1-sol', output_type=[str, DeferredToolRequests])

@agent.tool
def update_file(ctx: RunContext, path: str, content: str) -> str:
    if path == '.env' and not ctx.tool_call_approved:
        raise ApprovalRequired(metadata={'reason': 'protected'})
    return f'File {path!r} updated: {content!r}'

@agent.tool_plain(requires_approval=True)
def delete_file(path: str) -> str:
    return f'File {path!r} deleted'

result = agent.run_sync('Delete `__init__.py`, write `Hello, world!` to `README.md`, and clear `.env`')
stored = ConversationTypeAdapter.dump_json(result.conversation)  # (1)

conversation = ConversationTypeAdapter.validate_json(stored)  # (2)
requests = conversation.deferred_tool_requests
assert requests is not None
print(requests.metadata)
#> {'update_file_dotenv': {'reason': 'protected'}}

results = requests.build_results(approvals={'update_file_dotenv': True, 'delete_file': False})  # (3)
result = agent.run_sync(
    'Now create a backup of README.md',
    conversation=conversation,
    deferred_tool_results=results,
)
print(result.conversation.deferred_tool_requests)  # (4)
#> None
```

Store the paused conversation, for example keyed by `result.conversation_id`.

Later — in another request, once someone has reviewed the pending calls — load it back.

[`build_results`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolRequests.build_results) checks each answer against the request it answers, so a stale or mistyped tool call ID fails here rather than in the run.

The run finished, so the conversation it hands back isn't waiting on anything.

*(This example is complete, it can be run “as is”)*

## Observing deferred tool calls in a stream

Like any other tool call, a deferred tool call emits a [`FunctionToolCallEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.FunctionToolCallEvent) into the [event stream](https://pydantic.dev/docs/ai/core-concepts/agent/#streaming-events-and-final-output) — but that event alone doesn’t tell a stream consumer that the call is paused waiting for interaction, or what kind of interaction is expected. Two additional [`AgentStreamEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.AgentStreamEvent) s carry that context:

- [`DeferredToolRequestsEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.DeferredToolRequestsEvent) — emitted once per batch of deferred calls, carrying the [`DeferredToolRequests`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolRequests). It’s emitted before any [`HandleDeferredToolCalls`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.HandleDeferredToolCalls) handler runs, so a consumer can for example notify a frontend that input is needed while the handler waits for it. If no handler resolves all of the requests, the run ends with the pending requests as its `DeferredToolRequests` output.
- [`DeferredToolResultsEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.DeferredToolResultsEvent) — emitted when a handler resolves (some of) the requests, carrying the [`DeferredToolResults`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolResults). The resolved calls then execute through the regular pipeline, emitting a [`FunctionToolResultEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.FunctionToolResultEvent) each. No event is emitted when results are instead provided to a new run via `deferred_tool_results`, as in that case the caller already knows them.

This keeps resolution and presentation decoupled: a handler can contain pure resolution logic (e.g. waiting for a person’s decision through a [resume token](https://pydantic.dev/docs/ai/capabilities/handle-deferred-tool-calls/#a-handler-that-takes-a-token)), while a stream consumer owns all communication with the frontend, without maintaining its own mapping of which tools are interactive.

Continuing the [handler example](#resolving-deferred-calls-with-a-handler) from above:

deferred\_tool\_events.py

```python
from pydantic_ai import DeferredToolRequestsEvent, DeferredToolResultsEvent

from deferred_tool_handler import agent

async def main():
    async with agent.run_stream_events(
        'Delete `__init__.py`, write `Hello, world!` to `README.md`, and clear `.env`'
    ) as events:
        async for event in events:
            if isinstance(event, DeferredToolRequestsEvent):
                print(f'Approvals needed: {[call.tool_name for call in event.requests.approvals]}')
                #> Approvals needed: ['update_file', 'delete_file']
            elif isinstance(event, DeferredToolResultsEvent):
                print(f'Resolved: {list(event.results.approvals)}')
                #> Resolved: ['update_file_dotenv', 'delete_file']
```

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*
