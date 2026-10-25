---
title: "Pi Durable, explained"
site: "Pi Pocket"
source: "https://tannermidd.github.io/pi-pocket/durable.html"
domain: "tannermidd.github.io"
language: "en"
description: "An interactive guide to the Pi Durable agent harness: commits, tasks, crash recovery, forks, extensions, compaction, and storage."
word_count: 2105
---

Earendil/Pi 1.0/ **@earendil-works/pi-durable** experimental

## Pi Durable

An agent harness that *stores each step before it shows the step.*

Pi Durable runs conversations with language models. It writes each step to storage as an atomic commit. Clients show only committed data. If the process stops, a new process opens the same storage and continues from the last commit. Each panel on this page is a working model. Use its controls to operate it.

commit log · one sequence of atomic commits entry task document submission

**Each step is a task.**

A task is a small state machine. It saves a checkpoint after each step. Model calls, tool calls, and compactions are tasks.

**Each change is one commit.**

One commit can add entries, change documents, and create tasks. Storage keeps all of the commit or none of it.

**Clients show only commits.**

Each client shows the committed state. A phone that connects again shows the same data as a laptop.

## Durable state for agent applications

The Pi coding agent is for one person in one terminal. It saves its session in a file. But a run is in the memory of the process. If the process stops, the run stops. Then you tell the agent to continue. Pi Durable is a harness for agent applications. These applications run for a long time, have more than one user, continue after a restart, and change their code during operation. The table compares Pi Durable with a usual agent loop that keeps its state in memory.

Comparison

| Event | Agent loop with state in memory | Pi Durable |
| --- | --- | --- |
| The process stops | The run, the partial answer, and the queue are lost. | A new process opens the storage and continues from the last checkpoint. |
| A client sends a request again | The agent can get the message two times. | The same `requestId` finds the submission that is in storage. |
| A second device connects | The device shows nothing until the next event. | The device gets the committed view. This view includes streamed text and running tools. |
| You try a different path | You must make a copy of the history yourself. | You fork from an entry. The fork gets the history up to that entry. Each document follows its fork policy. |
| The tool code changes | You restart the process. The current run stops. | You install the new extension. Running calls use the old code. The next call uses the new code. |
| The context is full | The agent stops to make a summary. | A background task makes a summary while the agent works. The harness adds it at the next boundary. |

## Five layers and one sequence of commits

The announcement defines a harness as "storage plus the machinery needed to run one or more conversations with large language models in parallel." Click a layer to see its parts.

Layersapproximately 15,000 lines of TypeScript

**pi-ai** Gives access to models and providers. Also does streaming and sign-in.

**ExecutionEnv** Gives tools access to files and shells. You can use one for each conversation.

## Stop the process during an answer

The harness answers an input with a chain of tasks. Each task adds entries to the transcript. The list below shows the chain from the README. The simulator under the list runs the same chain. You can kill the process at any step and then open it again.

submit(input) → pi.user

pi.generation → pi.systemonly if the prompt or tools changed, pi.assistantwith tool calls

pi.tool × n → pi.tool-result × nthe generation owns these tasks and waits for them

pi.generation → pi.assistantthe answer → submission done

dashed in memory only #n commit in storage

#### Process memoryalive

#### Storage: session.sqliteseq 0

#### Transcript entriesconversation root

#### Tasksby owner

#### Documentsbuilt in, and the submission

1. Click **Run**. Each commit goes into storage before the transcript shows it.
2. Click **Reset** and **Run**. When `bash` shows output, click **Kill process**. Then click **Reopen and resume()**. The run continues without a click.
3. Set `replay: "safe"` on `bash` before `bash` starts. Do step 2 again. `bash` runs again. `read` keeps the default value, `"unsafe"`.
4. Kill the process during the first answer, after a flush. The committed part stays in the transcript as an aborted answer.
5. Kill the process when a chunk is dashed. The harness loses only that chunk. A chunk is approximately 100 ms of output. A chunk of large tool output can be longer.

## Retry without a duplicate

A phone sends "Deploy to staging". The server stores the message and starts the work. Then the network loses the reply, so the phone sends the message again. Without an idempotency key, the agent deploys two times. With a `requestId`, the second submit finds the first submission.

#### Clientphone

#### Storage · submissions

```shell
root.submit({ type: "input", content: "Deploy to staging", requestId: "deploy-7f3a" }, ctx)
// After a restart or a retry, the same requestId returns the stored submission.
// again.id === submission.id. Use harness.submission(id) to get it again and wait.
```

## Input to a busy conversation

A conversation is busy while a run continues. A submission during a run goes into the pi.inbox document. The harness adds it to the transcript at a boundary. A boundary is the end of a tool round or the end of the run. The submission type sets the boundary. A submission to an idle conversation goes into the transcript immediately.

Run in progress

#### pi.inboxqueued

#### Placed in the transcript

| Submission type | Boundary | Result |
| --- | --- | --- |
| whenBusy: "steer" | End of the current tool round | The submission joins the current run. The next model request includes it. If the run ends first, the steer starts the next run. |
| follow-up default | End of the run | The submission starts the next run. |
| type: "write" | Next boundary | The harness adds an entry. It does not send a model request. |
| whenBusy: "reject" | None | `submit()` throws `ConversationBusy`. |

Each boundary adds all queued writes. By default, it also adds one steer. The end of a run also adds one follow-up. To add all queued steers or follow-ups at one time, set `steeringMode: "all"` or `followUpMode: "all"` in the harness settings. Use `submission.abort()` to remove a queued submission.

## Task ownership and abort order

Each task has an owner. The owner is a conversation or a different task. A task can create child tasks and then commit a `waiting` state. A waiting task runs no code until its child tasks are complete. The README example is a checkout that charges four cards at the same time. Click a button to run a case.

#### Task treeidle

#### Event log

```shell
// The "pay" phase creates four Payment tasks that the checkout owns. Then it waits.
pay: async (task, runtime, ctx) => {
  await runtime.commit(async (tx) => {
    const payments = [];
    for (const card of task.input.cards)
      payments.push(await tx.createTask(Payment, { card }, { ownership: { kind: "task", taskId: task.id } }));
    return { status: "waiting", checkpoint: { phase: "decide", payments }, on: payments, policy: "failFast" };
  }, ctx);
},
// The abort handler of each Payment refunds its charge. Abort runs on child tasks first.
```

**Subagents use the same ownership model.** A subagent is a conversation that the task of a tool call owns. If the tool call aborts or fails, the child conversation also aborts. The parent stays busy until the child is idle.

A task with `{ background: true }` is a boundary. The work that it owns continues after the parent aborts, and it does not keep the parent busy. Persistent background subagents use this boundary. An anchor task owns each child conversation. A reporter task sends each answer to the parent as a follow-up.

Task statuscommitted statuses in the task graph

The outcome `faulted` shows that a task broke the task rules, for example with an error that it did not catch. If the harness aborts a task that no installed code can run, the task goes directly from pending or waiting to terminal, with the outcome `orphaned`.

## Documents and forks

A document is typed JSON. The harness stores it with the transcript. One commit can change documents and add entries together. Thus, if a commit changes a document and the transcript, the two agree after a crash. Each document kind has a **scope**: session, conversation, or task. A conversation document also has a **history** setting (`latest` or `rewindable`) and a **fork policy**. The fork policy sets the start value in a fork. Select a fork point and a fork policy.

#### Parent transcriptclick an entry to fork at it

```shell
const Todos = defineDoc<{ items: string[] }>({
  kind: "app.todos", version: 1, scope: "conversation",
  history: "rewindable", // "asOf" needs "rewindable": it reads old values
  fork: "asOf",  // what a fork starts with
  initial: () => ({ items: [] }),
});
await root.commit(async (tx) => { (await tx.doc(Todos, root.id)).items.push("write docs"); }, ctx);
```

The harness has five built-in documents:

- pi.agent: model, thinking level, extensions, tools, instructions, and working directory. It stores the model as a provider and a model ID. It stores extensions and tools as names, not as code.
- pi.provider: a UUIDv7 session identity for provider prompt caches.
- pi.live: the current run, the streamed answer, the tools that run, and the compactions that are in progress.
- pi.inbox: queued submissions.
- pi.usage: tokens and cost for each model, and for each tool that reports usage. Failed and aborted attempts are included.

A fork gets a new provider identity.

## Extensions, hooks, and live reload

An extension is a named set of **tools**, system prompt **sections**, **hooks**, **wraps**, and **tasks**. A conversation stores extension names. It does not store code. The harness gets the code from the registry each time it uses an extension. Click a hook to see where it runs.

Hook points

GenerationTask

ToolTask

Live reload: registry.install()

#### Registryin memory, not in storage

#### Tool calls

Two selected extensions can have a tool with the same name. Then the tool of the later extension replaces the earlier tool. `wrapTool()` adds behavior to the tool that remains. For example, some conversations can use a `bash` tool that runs in a Python virtualenv. A timing wrapper can then measure the `bash` tool of each conversation.

## Background compaction

When a conversation gets long, a compaction task makes a summary of older entries. The task adds a pi.compaction entry at the end of the transcript. This entry points to the first entry that the task keeps. After this, the model gets the summary instead of the entries before that entry. The agent continues to work during the compaction. Storage keeps the older entries. Thus your tools can still read them. Move the slider to change the number of tokens.

Context window: 200,000 tokens

tokens in usebackground compaction range (backgroundTokens)reserve range: the next request waits (reserveTokens)

```shell
settings: { compaction: {
  enabled: true,
  reserveTokens: 16384,     // above window - reserve, the next request waits for a compaction
  keepRecentTokens: 20000,  // roughly how much recent context stays verbatim
  backgroundTokens: 32768,  // this far below that, a compaction starts in the background
} }
```

## Clients show committed state

A UI gets all of its data from committed state. `viewState()` gives a live read-only view. `watch()` gives the same view and the operations of each commit, one callback at a time. A client that connects late gets the current view. The harness does not replay old commits.

One conversation, more than one client

A slow watch keeps a maximum of 100 frames that it did not deliver. After that, the harness replaces these frames with one frame that contains the newest view. The harness commits partial answers and tool output a maximum of one time every 100 ms. For large tool output, the interval is longer. `watchEvents()` makes coding-agent events from commits, for example `message_update` and `tool_execution_start`.

## Storage backends

With SQLite, the harness keeps only the working set in memory. Older messages stay on disk until the harness needs them. The JSONL backend keeps all of its records in memory. Use only one process for a storage at a time. The storage does not prevent access by a second process.

tests and demos

### Memory

The harness does not persist data.

MemoryStorage usual choice

### SQLite

One database file in WAL mode with `synchronous = NORMAL`. Commits stay after a process crash. A power failure or host failure can lose the newest commit.

openNodeSqliteStorage(file) append-only

### JSONL

Append-only files in one directory. Set `{ fsync: true }` to flush the data before each commit marker.

openNodeJsonlStorage(dir, ctx)

The SQLite and JSONL cores do not use Node APIs. They run on Bun or in Cloudflare Durable Objects with a small database or file-system adapter. A custom backend can use the conformance test suite in `/testing`. The SQLite schema has these tables:

conversationsentriesdocumentsdocument\_revisionstaskssubmissionsrecord\_idsdurable\_metadatadurable\_schema
