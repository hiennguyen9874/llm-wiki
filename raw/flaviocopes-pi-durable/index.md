---
title: "How to build agents that survive crashes with Pi Durable"
author: "Flavio Copes"
site: "Flavio Copes"
published: 2026-10-16T14:30:00.000Z
source: "https://flaviocopes.com/pi-durable/"
domain: "flaviocopes.com"
language: "en"
description: "Build a durable TypeScript agent with Pi Durable and SQLite. Test crash recovery, avoid duplicate requests, and understand which tools can safely run again."
word_count: 3149
---

Build a durable TypeScript agent with Pi Durable and SQLite. Test crash recovery, avoid duplicate requests, and understand which tools can safely run again.

\~~~

An agent can spend twenty minutes investigating a problem, then disappear when its Node process crashes. A saved chat helps you explain what happened. Recovering the unfinished work needs more information: which tool was running, what already finished, and which requests are still waiting.

[Pi Durable](https://github.com/earendil-works/pi/tree/main/packages/durable) stores that information as the agent works. Reopen its storage after a process crash, and it can continue the unfinished run.

It’s a TypeScript library from Earendil, the team behind [Pi](https://flaviocopes.com/pi/). You use it to build your own agent application, including the tools and interface you want. The regular Pi terminal app remains available for interactive coding.

The [Syntax video “My Code Fixes Itself Now”](https://www.youtube.com/watch?v=BLRReTwV8Fc) shows a useful application. A Sentry error starts an agent, which investigates the bug and prepares a pull request. The demonstration also stops and resumes the work. Sentry, GitHub, and the screens around that agent are application code built around Pi Durable.

Let’s build something smaller so we can see how recovery works. We’ll give an agent a read-only service-status tool, store its work in SQLite, kill the process while the tool runs, then restart it with the same request.

There are eight interactive drawings throughout this tutorial. Click a drawing, or focus it and press Enter or Space, to move through its states.

> Pi Durable is experimental. These examples follow the package API checked in October 2026. Keep your package lockfile, because the API can change between releases.

## What Pi Durable stores

An agent application has a model, tools the model can call, and code that runs their conversation. That surrounding code is often called a **harness**.

Pi Durable provides the harness. It commits conversation entries and execution state to storage as work progresses. A model request and its tool calls run as durable tasks.

You provide the model credentials, tool implementations, and somewhere to store the data.

Fig 1 · 1/4The pieces of a durable agent

<svg viewBox="0 0 640 320" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><rect stroke="currentColor" fill="none" x="20" y="110" width="140" height="85" rx="3"></rect><text fill="currentColor" x="34" y="135" text-anchor="start" style="font-size:13px">YOUR APP</text> <text fill="currentColor" x="34" y="165" text-anchor="start" style="font-size:16px">Input</text> <rect stroke="currentColor" fill="none" x="205" y="90" width="205" height="125" rx="3"></rect><text fill="currentColor" x="219" y="115" text-anchor="start" style="font-size:13px">HARNESS</text> <text fill="currentColor" x="219" y="145" text-anchor="start" style="font-size:16px">Conversation</text> <text fill="currentColor" x="219" y="170" text-anchor="start" style="font-size:16px">Tasks + tools</text> <rect stroke="currentColor" fill="none" x="465" y="15" width="155" height="75" rx="3"></rect><text fill="currentColor" x="479" y="40" text-anchor="start" style="font-size:13px">MODEL</text> <text fill="currentColor" x="479" y="70" text-anchor="start" style="font-size:16px">Provider</text> <rect stroke="currentColor" fill="none" x="465" y="115" width="155" height="85" rx="3"></rect><text fill="currentColor" x="479" y="140" text-anchor="start" style="font-size:13px">ENVIRONMENT</text> <text fill="currentColor" x="479" y="170" text-anchor="start" style="font-size:16px">Files / shell</text> <rect stroke="currentColor" fill="none" x="465" y="225" width="155" height="75" rx="3"></rect><text fill="currentColor" x="479" y="250" text-anchor="start" style="font-size:13px">STORAGE</text> <text fill="currentColor" x="479" y="280" text-anchor="start" style="font-size:16px">Checkpoints</text> <path fill="none" d="M160 150 L205 150" style="stroke:currentColor"></path><polygon points="205,150 197.10175694298664,154.31482984743784 197.10175694298664,145.68517015256216" style="fill:currentColor"></polygon><path fill="none" d="M410 105 L458 56" style="stroke:currentColor"></path><polygon points="458,56 455.5553045069138,64.66160862346504 449.39063304953237,58.62274678766284" style="fill:currentColor"></polygon><path fill="none" d="M410 155 L458 155" style="stroke:currentColor"></path><polygon points="458,155 450.10175694298664,159.31482984743784 450.10175694298664,150.68517015256216" style="fill:currentColor"></polygon><path fill="none" d="M410 200 L458 260" style="stroke:currentColor"></path><polygon points="458,260 449.6966906319846,256.5279611841127 456.43532272382066,251.13705551064388" style="fill:currentColor"></polygon><text fill="currentColor" x="20" y="270" text-anchor="start" style="font-size:15px">Choose each part for your application</text></svg>

A client submits a message

The model still runs through its provider. SQLite stores the agent’s state locally. Putting a harness on your laptop doesn’t move an OpenAI model onto your laptop.

This also explains why “durable” doesn’t mean the process stays alive forever. When the process is down, work stops. A supervisor, container platform, or you must start another process. Pi Durable gives that process the saved work to resume.

## Create the project

Use a current Node.js LTS release with the built-in `node:sqlite` module. You’ll also need an OpenAI API key with access to the model used below. Model calls are billed through that API account.

Create an empty directory:

```bash
mkdir pi-durable-demo
cd pi-durable-demo
npm init -y
npm pkg set type=module
npm install --ignore-scripts @earendil-works/pi-durable @earendil-works/pi-ai @earendil-works/chord
npm install --save-dev --ignore-scripts tsx typescript @types/node
```

`pi-ai` handles model access. `chord` provides the state and cancellation primitives Pi Durable uses. `tsx` runs our TypeScript files.

Our project will have two source files:

```text
pi-durable-demo/
  agent.ts
  tools.ts
```

Running it will also create `agent.sqlite` and possibly SQLite journal files. Keep those out of Git, along with credentials:

```plaintext
node_modules/
.env
agent.sqlite*
```

Save that as `.gitignore`.

## Give the agent a tool

We need a tool whose behavior is easy to inspect. Our `service_status` tool looks up a service in a small fixture. The website is healthy; checkout is degraded after a deployment.

It deliberately waits ten seconds before returning. That gives us time to kill the process during the check.

Save this complete file as `tools.ts`:

```typescript
import { setTimeout as delay } from 'node:timers/promises'
import { Type } from '@earendil-works/pi-ai'
import { defineExtension, defineTool } from '@earendil-works/pi-durable'

const services = {
  website: { status: 'healthy', lastDeploy: 'deploy-104' },
  checkout: { status: 'degraded', lastDeploy: 'deploy-105' },
}

const serviceStatus = defineTool({
  name: 'service_status',
  description: 'Read the demo status for website or checkout',
  parameters: Type.Object({
    service: Type.Union([
      Type.Literal('website'),
      Type.Literal('checkout'),
    ]),
  }),
  replay: 'safe',
  execute: async ({ service }, api, context) => {
    api.output(`Checking ${service}...\n`)
    console.log(`Tool started: ${service}`)
    await delay(10000, undefined, { signal: context.abortSignal })
    return {
      output: [{ type: 'text', text: JSON.stringify(services[service]) }],
    }
  },
})

export const StatusTools = defineExtension({
  name: 'status-tools',
  tools: [serviceStatus],
})
```

This is demo data. We aren’t checking a real website or contacting a monitoring service.

`parameters` describes the allowed arguments and validates them before execution. The model can request `website` or `checkout`.

`api.output()` publishes progress while the tool runs. The returned `output` contains the result the model receives. `context.abortSignal` lets the delay stop when the harness cancels this call.

The important setting is `replay: 'safe'`. It tells Pi Durable that this tool can run again after an interrupted execution. Reading this fixture has no external side effect, so repeating it is safe.

The extension gives the tool a stable name in the registry. Reinstall the same extension whenever you open this agent’s storage.

## Open SQLite and submit a request

Now we can connect the model, tool registry, and database.

Save this complete file as `agent.ts`:

```typescript
import { BACKGROUND_CONTEXT } from '@earendil-works/chord/context'
import { createModels } from '@earendil-works/pi-ai/models'
import { openaiProvider } from '@earendil-works/pi-ai/providers/openai'
import {
  AssistantEntry,
  createRegistry,
  Harness,
} from '@earendil-works/pi-durable'
import { openNodeSqliteStorage } from '@earendil-works/pi-durable/storage/sqlite/node'
import { StatusTools } from './tools.js'

const requestId = process.argv[2]
const prompt = process.argv.slice(3).join(' ')
if (!requestId || !prompt) {
  throw new Error('Pass a request ID followed by a prompt')
}
if (!process.env.OPENAI_API_KEY) {
  throw new Error('Set OPENAI_API_KEY before running the agent')
}

const context = BACKGROUND_CONTEXT
const models = createModels()
models.setProvider(openaiProvider())
const registry = createRegistry()
registry.install(StatusTools)

const harness = await Harness.open(
  await openNodeSqliteStorage('./agent.sqlite'),
  { models, registry },
  context,
)

try {
  const root = await harness.root(context, {
    agent: {
      model: { provider: 'openai', modelId: 'gpt-6-sol' },
      instructions: 'Use service_status for service questions. Explain the demo results briefly. Never claim to repair or deploy anything.',
    },
  })
  harness.resume()
  const submission = await root.submit(
    { type: 'input', content: prompt, requestId },
    context,
  )
  console.log(`Submission: ${submission.id}`)
  const settled = await submission.wait(context)
  if (settled.status !== 'done' || settled.type !== 'input') {
    throw new Error(`The input was not answered: ${JSON.stringify(settled)}`)
  }
  const answer = await root.commit(
    (tx) => tx.entry(AssistantEntry, settled.answer),
    context,
  )
  for (const message of answer?.model ?? []) {
    if (message.role !== 'assistant') continue
    for (const part of message.content) {
      if (part.type === 'text') console.log(part.text)
    }
  }
} finally {
  await harness.close(context)
}
```

Notice the `./tools.js` import. That’s the output path TypeScript resolves to `tools.ts` when using Node’s module conventions; `tsx` handles it while running the source.

`harness.root()` creates the root conversation on first use. Opening the same database returns that conversation again. Its initial agent settings apply when it is created. To change an existing conversation later, use `root.configure()`.

`harness.resume()` starts recovery of pending tasks. Submitting or waiting also starts the scheduler; the explicit call makes the restart behavior visible here.

A **submission** is the request we admitted to the conversation. Its ID lets us identify that same request after a restart. `wait()` waits for an answer, and the final transaction reads the assistant entry containing it.

The `finally` block closes the harness on an ordinary exit. A hard process kill skips that block, which is exactly what we want to test later.

## Run the agent

Put your API key in the shell environment. For example, in zsh you can enter it without echoing it or putting the key in your command history:

```bash
read -rs 'OPENAI_API_KEY?OpenAI API key: '
export OPENAI_API_KEY
```

Run a status check:

```bash
npx tsx agent.ts incident-105 'Use service_status to check checkout. Explain the result.'
```

`incident-105` is our application’s request ID. It is separate from the submission ID printed by Pi Durable.

The tool prints `Tool started: checkout`, waits, then returns the fixture. The wording of the model’s answer varies, but it should explain that checkout is degraded after `deploy-105`.

The agent has only the tool we installed. It has no shell, file-editing tool, deployment credentials, or ability to repair checkout.

You can type-check both files with:

```bash
npx tsc --noEmit --strict --skipLibCheck --module nodenext --target esnext agent.ts tools.ts
```

## Kill it halfway through

Now let’s interrupt a new request while its tool is running.

In your first terminal, run:

```bash
npx tsx agent.ts incident-106 'Use service_status to check checkout. Explain the result.'
```

Wait for `Tool started: checkout`.

In a second terminal, find the Node process running this example:

```bash
pgrep -fl 'agent.ts'
```

Identify the Node process executing `agent.ts`, then send `kill -9` followed by that process’s numeric PID. If `tsx` has a launcher and a child, target the child executing the TypeScript file. Check the command before killing it.

Wait until that process has exited. From the original project directory, restart with the exact same command:

```bash
npx tsx agent.ts incident-106 'Use service_status to check checkout. Explain the result.'
```

The submission ID should match the one printed before the crash. Our replay-safe tool starts again, waits ten seconds, and returns its result.

Fig 2 · 1/4What happens after a crash

<svg viewBox="0 0 640 300" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path fill="none" d="M45 60 L595 60" style="stroke:currentColor"></path><polygon points="595,60 587.1017569429866,64.31482984743782 587.1017569429866,55.68517015256217" style="fill:currentColor"></polygon><circle cx="70" cy="60" r="8" style="fill:currentColor"></circle><text fill="currentColor" x="70" y="35" text-anchor="middle" style="font-size:15px">Save</text> <circle cx="235" cy="60" r="8" style="fill:currentColor"></circle><text fill="currentColor" x="235" y="35" text-anchor="middle" style="font-size:15px">Crash</text> <circle cx="400" cy="60" r="8" style="fill:currentColor"></circle><text fill="currentColor" x="400" y="35" text-anchor="middle" style="font-size:15px">Reopen</text> <circle cx="565" cy="60" r="8" style="fill:currentColor"></circle><text fill="currentColor" x="565" y="35" text-anchor="middle" style="font-size:15px">Resume</text> <rect stroke="currentColor" fill="none" x="25" y="105" width="280" height="105" rx="3"></rect><text fill="currentColor" x="39" y="130" text-anchor="start" style="font-size:13px">PERSISTENT STORAGE</text> <text fill="currentColor" x="39" y="160" text-anchor="start" style="font-size:16px">Checkpoint: saved</text> <text fill="currentColor" x="39" y="185" text-anchor="start" style="font-size:16px">Task: in progress</text> <rect stroke="currentColor" fill="none" x="345" y="105" width="270" height="105" rx="3"></rect><text fill="currentColor" x="359" y="130" text-anchor="start" style="font-size:13px">FIRST PROCESS</text> <text fill="currentColor" x="359" y="160" text-anchor="start" style="font-size:16px">Running service_status</text> <path fill="none" d="M345 180 L305 180" style="stroke:currentColor"></path><polygon points="305,180 312.89824305701336,175.68517015256216 312.89824305701336,184.31482984743784" style="fill:currentColor"></polygon><rect stroke="currentColor" fill="none" x="25" y="240" width="590" height="45" rx="3"></rect><text fill="currentColor" x="320" y="269" text-anchor="middle" style="font-size:16px">Continue from the last stored checkpoint</text></svg>

A task saves its checkpoint

Pi Durable resumes from durable checkpoints. It doesn’t restore a suspended JavaScript stack at the exact instruction that was interrupted. Our tool function starts over because it was interrupted before its result was committed.

An interrupted model request can also be sent again. A stored partial answer is marked as aborted; it isn’t a completed answer. Another model request can mean another API charge.

The recovery path here was tested with SQLite and a scripted provider from Pi’s testing utilities. The test killed a subprocess inside the real tool, reopened its database, and checked the submission ID. That verifies persistence and replay behavior without depending on a live model’s wording. It doesn’t measure model quality or exercise a real monitoring integration.

## Retry a request without creating a second job

Run the completed `incident-106` command again.

It should print the same submission ID and saved answer. It shouldn’t start the tool again.

Fig 3 · 1/3Retry input without submitting it twice

<svg viewBox="0 0 640 300" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><rect stroke="currentColor" fill="none" x="20" y="85" width="225" height="115" rx="3"></rect><text fill="currentColor" x="34" y="110" text-anchor="start" style="font-size:13px">CLIENT INPUT</text> <text fill="currentColor" x="34" y="140" text-anchor="start" style="font-size:16px">incident-106</text> <text fill="currentColor" x="34" y="165" text-anchor="start" style="font-size:16px">Submit work</text> <path fill="none" d="M245 140 L300 140" style="stroke:currentColor"></path><polygon points="300,140 292.10175694298664,144.31482984743784 292.10175694298664,135.68517015256216" style="fill:currentColor"></polygon><rect stroke="currentColor" fill="none" x="300" y="35" width="320" height="210" rx="3"></rect><text fill="currentColor" x="320" y="65" text-anchor="start" style="font-size:13px">ONE CONVERSATION</text> <rect stroke="currentColor" fill="none" x="320" y="85" width="280" height="55" rx="3"></rect><text fill="currentColor" x="335" y="119" text-anchor="start" style="font-size:16px">incident-106 → A</text> <rect stroke="currentColor" fill="none" x="320" y="165" width="280" height="55" rx="3"></rect><text fill="currentColor" x="335" y="199" text-anchor="start" style="font-size:15px">No second submission</text> <text fill="currentColor" x="320" y="285" text-anchor="middle" style="font-size:16px">This deduplicates input to the harness</text></svg>

incident-106 creates a submission

The `requestId` deduplicates admission of a submission. Retrying delivery of the same logical job should reuse its ID. A genuinely new status check needs a new ID, even if its prompt is identical.

Don’t reuse an old ID for a different prompt. You’re identifying the original job, rather than asking for an updated answer.

For a webhook application, derive this ID from a stable event identifier. If your policy is one investigation per incident, keep an incident-to-investigation mapping too. Monitoring systems can send several different events about the same incident.

## Decide which tools may run again

Imagine replacing our fixture with an email sender.

The email provider accepts the message. Then the process dies before Pi Durable commits the tool result. When it restarts, the local database can’t tell whether the email went out.

Automatically running that tool again could send a duplicate.

Fig 4 · 1/3A crash cannot undo an external action

<svg viewBox="0 0 640 315" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><rect stroke="currentColor" fill="none" x="20" y="100" width="200" height="105" rx="3"></rect><text fill="currentColor" x="34" y="125" text-anchor="start" style="font-size:13px">INTERRUPTED CALL</text> <text fill="currentColor" x="34" y="155" text-anchor="start" style="font-size:16px">Result not saved</text> <rect stroke="currentColor" fill="none" x="320" y="25" width="300" height="95" rx="3"></rect><text fill="currentColor" x="334" y="50" text-anchor="start" style="font-size:13px">SAFE TO REPLAY</text> <text fill="currentColor" x="334" y="80" text-anchor="start" style="font-size:16px">Read service status</text> <text fill="currentColor" x="334" y="105" text-anchor="start" style="font-size:16px">Run the read again</text> <rect stroke="currentColor" fill="none" x="320" y="165" width="300" height="105" rx="3"></rect><text fill="currentColor" x="334" y="190" text-anchor="start" style="font-size:13px">EXTERNAL SIDE EFFECT</text> <text fill="currentColor" x="334" y="220" text-anchor="start" style="font-size:16px">Send an email</text> <text fill="currentColor" x="334" y="245" text-anchor="start" style="font-size:16px">Check before trying again</text> <path fill="none" d="M220 125 L310 75" style="stroke:currentColor"></path><polygon points="310,75 305.1911599777821,82.60756581573341 301.0002267484886,75.06388600300508" style="fill:currentColor"></polygon><path fill="none" d="M220 185 L310 215" style="stroke:currentColor"></path><polygon points="310,215 301.14259972446996,216.59576325281677 303.871537731266,208.40894923242854" style="fill:currentColor"></polygon><text fill="currentColor" x="20" y="290" text-anchor="start" style="font-size:15px">Input deduplication does not deduplicate email</text></svg>

A tool call is interrupted

A tool’s default replay policy is unsafe. Leave it that way for an action you cannot safely repeat. After an interruption, the harness reports an interrupted result to the model instead of automatically rerunning that call.

That still leaves an application decision. The model could request a fresh tool call. Your application must prevent that from repeating an action whose outcome is uncertain.

For actions such as sending email or creating a pull request, use an operation ID and the external service’s idempotency mechanism when available. Otherwise, reconcile against the external system before allowing another attempt. If you cannot establish the outcome, ask a person to resolve it.

Only declare an effectful tool replay-safe once its implementation makes repeated execution safe.

| Operation | What to check before enabling replay |
| --- | --- |
| Read service status | Repeating the read is acceptable; the answer may have changed |
| Search issues | The search has no mutation; repeated queries may still cost money |
| Send an email | The sender deduplicates the same operation ID |
| Create a pull request | The app finds or reuses the existing operation’s PR |
| Deploy a release | The deployment system reconciles the operation and its outcome |

Submission deduplication and tool idempotency solve different parts of this problem. A stable `requestId` alone doesn’t make an external action happen exactly once.

## Separate the transcript from the work

The transcript records what happened in the conversation. Tasks record the execution needed to get to an answer.

A model can request a tool. That tool runs as a task owned by the generation task. Once the tool finishes, another model turn can interpret its result and answer the user.

Fig 5 · 1/3Execution and conversation are related

<svg viewBox="0 0 640 315" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><text fill="currentColor" x="25" y="25" text-anchor="start" style="font-size:13px">TASKS: WHAT THE HARNESS RUNS</text> <rect stroke="currentColor" fill="none" x="25" y="45" width="170" height="80" rx="3"></rect><text fill="currentColor" x="39" y="70" text-anchor="start" style="font-size:13px">MODEL REQUEST</text> <text fill="currentColor" x="39" y="100" text-anchor="start" style="font-size:16px">Call the model</text> <rect stroke="currentColor" fill="none" x="235" y="45" width="170" height="80" rx="3"></rect><text fill="currentColor" x="249" y="70" text-anchor="start" style="font-size:13px">TOOL CALL</text> <text fill="currentColor" x="249" y="100" text-anchor="start" style="font-size:16px">service_status</text> <rect stroke="currentColor" fill="none" x="445" y="45" width="170" height="80" rx="3"></rect><text fill="currentColor" x="459" y="70" text-anchor="start" style="font-size:13px">MODEL REQUEST</text> <text fill="currentColor" x="459" y="100" text-anchor="start" style="font-size:16px">Call the model</text> <path fill="none" d="M195 85 L230 85" style="stroke:currentColor"></path><polygon points="230,85 222.10175694298664,89.31482984743782 222.10175694298664,80.68517015256218" style="fill:currentColor"></polygon><path fill="none" d="M405 85 L440 85" style="stroke:currentColor"></path><polygon points="440,85 432.10175694298664,89.31482984743782 432.10175694298664,80.68517015256218" style="fill:currentColor"></polygon><path fill="none" d="M110 130 L110 150" style="stroke:currentColor"></path><polygon points="110,150 105.68517015256216,142.10175694298664 114.31482984743782,142.10175694298664" style="fill:currentColor"></polygon><path fill="none" d="M320 130 L320 150" style="stroke:currentColor"></path><polygon points="320,150 315.6851701525622,142.10175694298664 324.3148298474378,142.10175694298664" style="fill:currentColor"></polygon><path fill="none" d="M530 130 L530 150" style="stroke:currentColor"></path><polygon points="530,150 525.6851701525621,142.10175694298664 534.3148298474379,142.10175694298664" style="fill:currentColor"></polygon><text fill="currentColor" x="25" y="170" text-anchor="start" style="font-size:13px">TRANSCRIPT: WHAT THE CONVERSATION RECORDS</text> <rect stroke="currentColor" fill="none" x="25" y="190" width="170" height="65" rx="3"></rect><text fill="currentColor" x="110" y="229" text-anchor="middle" style="font-size:15px">Tool request</text> <rect stroke="currentColor" fill="none" x="235" y="190" width="170" height="65" rx="3"></rect><text fill="currentColor" x="320" y="229" text-anchor="middle" style="font-size:15px">Status result</text> <rect stroke="currentColor" fill="none" x="445" y="190" width="170" height="65" rx="3"></rect><text fill="currentColor" x="530" y="229" text-anchor="middle" style="font-size:15px">Answer</text> <text fill="currentColor" x="320" y="292" text-anchor="middle" style="font-size:16px">Task checkpoints let execution recover</text></svg>

The model request runs as a task

Saving only chat messages is insufficient for recovery. The application also needs to know about work that has started but hasn’t produced a final message yet.

Pi Durable can store your own typed application documents beside the transcript. A commit can update those documents, append entries, and create tasks atomically. That is useful for an incident’s investigation status, for example.

That transaction covers Pi Durable’s storage. It doesn’t include a remote GitHub or email API call in the same atomic operation.

## Connect more than one screen

The terminal script is one way to submit work. A web interface or Slack integration can submit to the same conversation through your application server.

Keep one process responsible for opening and owning a particular store. Other clients connect to that process. Pi Durable doesn’t provide cross-process locking for several independent harnesses opening the same database.

Fig 6 · 1/3Several clients, one storage owner

<svg viewBox="0 0 640 310" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><rect stroke="currentColor" fill="none" x="20" y="30" width="170" height="90" rx="3"></rect><text fill="currentColor" x="34" y="55" text-anchor="start" style="font-size:13px">TERMINAL</text> <text fill="currentColor" x="34" y="85" text-anchor="start" style="font-size:16px">Client A</text> <rect stroke="currentColor" fill="none" x="20" y="190" width="170" height="90" rx="3"></rect><text fill="currentColor" x="34" y="215" text-anchor="start" style="font-size:13px">WEB UI</text> <text fill="currentColor" x="34" y="245" text-anchor="start" style="font-size:16px">Client B</text> <rect stroke="currentColor" fill="none" x="270" y="95" width="175" height="115" rx="3"></rect><text fill="currentColor" x="284" y="120" text-anchor="start" style="font-size:13px">ONE PROCESS</text> <text fill="currentColor" x="284" y="150" text-anchor="start" style="font-size:16px">Harness</text> <text fill="currentColor" x="284" y="175" text-anchor="start" style="font-size:16px">Storage owner</text> <rect stroke="currentColor" fill="none" x="500" y="105" width="120" height="95" rx="3"></rect><text fill="currentColor" x="514" y="130" text-anchor="start" style="font-size:13px">STORAGE</text> <text fill="currentColor" x="514" y="160" text-anchor="start" style="font-size:16px">SQLite</text> <path fill="none" d="M190 75 L260 125" style="stroke:currentColor"></path><polygon points="260,125 251.064991354052,123.92036094140917 256.080879167512,116.89811800256516" style="fill:currentColor"></polygon><path fill="none" d="M190 235 L260 175" style="stroke:currentColor"></path><polygon points="260,175 256.8112608545196,183.4161714967128 251.19515276923389,176.86404539721278" style="fill:currentColor"></polygon><path fill="none" d="M445 155 L490 155" style="stroke:currentColor"></path><polygon points="490,155 482.10175694298664,159.31482984743784 482.10175694298664,150.68517015256216" style="fill:currentColor"></polygon><text fill="currentColor" x="380" y="270" text-anchor="middle" style="font-size:15px">Clients share the owning process</text></svg>

The terminal connects to the owner

For a UI, `root.viewState(context)` exposes a subscribable conversation view. It includes committed entries, running tool output, and queued inputs. A reconnecting client can show the current state without reconstructing it from a private stream it might have missed.

Your server still provides transport, authentication, and authorization. Installing the package doesn’t create a hosted multiplayer app.

A message submitted while the conversation is busy becomes a follow-up by default. A steering input can join the current work at a tool-round boundary:

```typescript
await root.submit({
  type: 'input',
  content: 'Check website as well before answering.',
  whenBusy: 'steer',
}, context)
```

This snippet belongs inside the open harness’s `try` block, where `root` and `context` are available. To send it during the current run, the application must accept another input while the first submission is still waiting.

Steering doesn’t instantly interrupt an executing tool. Also, cancelling a wait only stops that caller from waiting. Explicitly aborting the conversation is a separate action.

## Keep the storage when you deploy

SQLite is convenient for a single Node process. It only helps across a deployment if the database remains available afterwards.

Fig 7 · 1/3Keep the database when the process goes

<svg viewBox="0 0 640 300" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><rect stroke="currentColor" fill="none" x="25" y="20" width="590" height="100" rx="3"></rect><text fill="currentColor" x="39" y="45" text-anchor="start" style="font-size:13px">RUNNING PROCESS</text> <text fill="currentColor" x="39" y="75" text-anchor="start" style="font-size:16px">Memory: active work</text> <path fill="none" d="M320 125 L320 170" style="stroke:currentColor"></path><polygon points="320,170 315.6851701525622,162.10175694298664 324.3148298474378,162.10175694298664" style="fill:currentColor"></polygon><rect stroke="currentColor" fill="none" x="25" y="180" width="590" height="105" rx="3"></rect><text fill="currentColor" x="39" y="205" text-anchor="start" style="font-size:13px">PERSISTENT DISK</text> <text fill="currentColor" x="39" y="235" text-anchor="start" style="font-size:16px">agent.sqlite</text> <text fill="currentColor" x="39" y="260" text-anchor="start" style="font-size:16px">Transcripts · tasks · queued input</text></svg>

The process holds the live working set

A container’s temporary filesystem can disappear when the container is replaced. Mount persistent storage, keep the same database path, and stop the old owner before starting its replacement.

Treat conversations and tool output as application data. They can contain private prompts and service information, so restrict access and back them up.

The package also ships JSONL and in-memory storage. In-memory storage is useful for tests, but it disappears with the process. Other runtimes can use adapters. A Cloudflare Durable Object is one possible host; Pi Durable doesn’t require Cloudflare.

Process-crash recovery also has limits. A deleted database cannot be resumed. SQLite’s shipped Node adapter uses WAL with `synchronous = NORMAL`, so a machine power failure can lose the newest commits even though a process crash is recoverable. Choose your storage and backup policy around the failures your application needs to survive.

## Long conversations still have context limits

Persistent storage can keep a conversation’s history longer than a model can accept in a request.

Pi Durable supports compaction to summarize older messages and make room for new work. The summary becomes part of what the model sees next.

Fig 8 · 1/3A smaller context keeps the full history

<svg viewBox="0 0 640 300" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><text fill="currentColor" x="25" y="30" text-anchor="start" style="font-size:13px">SAVED HISTORY</text> <rect stroke="currentColor" fill="none" x="25" y="50" width="590" height="65" rx="3"></rect><rect stroke="currentColor" fill="none" x="40" y="65" width="55" height="35" rx="3"></rect><rect stroke="currentColor" fill="none" x="110" y="65" width="55" height="35" rx="3"></rect><rect stroke="currentColor" fill="none" x="180" y="65" width="55" height="35" rx="3"></rect><rect stroke="currentColor" fill="none" x="250" y="65" width="55" height="35" rx="3"></rect><rect stroke="currentColor" fill="none" x="320" y="65" width="55" height="35" rx="3"></rect><rect stroke="currentColor" fill="none" x="390" y="65" width="55" height="35" rx="3"></rect><rect stroke="currentColor" fill="none" x="460" y="65" width="55" height="35" rx="3"></rect><rect stroke="currentColor" fill="none" x="530" y="65" width="55" height="35" rx="3"></rect><text fill="currentColor" x="25" y="145" text-anchor="start" style="font-size:16px">All messages remain in storage</text> <path fill="none" d="M175 155 L175 205" style="stroke:currentColor"></path><polygon points="175,205 170.68517015256216,197.10175694298664 179.31482984743784,197.10175694298664" style="fill:currentColor"></polygon><text fill="currentColor" x="320" y="200" text-anchor="start" style="font-size:13px">MODEL CONTEXT</text> <rect stroke="currentColor" fill="none" x="25" y="220" width="280" height="55" rx="3"></rect><text fill="currentColor" x="165" y="254" text-anchor="middle" style="font-size:15px">Older messages</text> <rect stroke="currentColor" fill="none" x="345" y="220" width="270" height="55" rx="3"></rect><text fill="currentColor" x="480" y="254" text-anchor="middle" style="font-size:15px">Recent messages</text> <text fill="currentColor" x="325" y="255" text-anchor="middle" style="font-size:20px">+</text></svg>

The conversation history grows

A summary can omit details. Store facts the application must preserve in structured documents or another appropriate database. For an incident investigation, that might include its incident ID, repository, and associated pull request.

Likewise, subagents need an implementation. Pi Durable provides conversations, ownership, tasks, and forks that you can build them from. Its [foreground and background subagent examples](https://github.com/earendil-works/pi/tree/main/packages/durable/test/examples) show the patterns.

## From this demo to an agent that investigates errors

The Syntax demonstration starts with an incoming monitoring event. Our command-line script starts with a request ID and a prompt. The next step is to have a webhook handler produce those values.

The application around it would:

1. Verify the webhook and check that the event belongs to a project it handles.
2. Find the incident’s existing investigation, or create one.
3. Submit the investigation with its stable request ID.
4. Give the agent narrow tools for reading the error and working on an isolated repository copy.
5. Run checks and prepare a pull request for review.
6. Record the PR and reconcile later events with that investigation.

Pi Durable supplies the persisted agent runtime inside that flow. You supply the event handling and the rules for changing code or contacting GitHub.

I would start with a tool that reads one real service’s status. Keep the crash test, add a test for an interrupted unsafe action, and check that a duplicate event creates no second investigation. Add the code-changing tools once those paths behave the way you expect.

The [upstream README](https://github.com/earendil-works/pi/blob/main/packages/durable/README.md) covers the APIs used here. Its [runnable examples](https://github.com/earendil-works/pi/tree/main/packages/durable/test/examples) go further into recovery, approvals, UI events, and subagents. Earendil’s [introduction to Pi Durable](https://earendil.com/posts/pi-durable/) explains the design behind them.

Tagged: [AI](https://flaviocopes.com/tags/ai/) · [All topics](https://flaviocopes.com/blog/#topics)

[Follow @flaviocopes](https://twitter.com/flaviocopes)

Want me to talk about your product? You can [sponsor this site](https://flaviocopes.com/sponsor/).

\~~~

Related posts about ai:

- [What changes when you stop opening the code editor?](https://flaviocopes.com/coding-without-the-editor/)
- [What would make an overnight agent useful?](https://flaviocopes.com/overnight-agent-work/)
