---
type: Concept
title: Pydantic AI code mode
description: Pydantic AI Harness CodeMode's sandbox and tool boundary, measured tradeoffs against direct tool calling, and operational risks.
tags: [pydantic-ai, ml, agents, sandboxing, benchmarks]
status: draft
created: 2026-11-17
generated: { by: llm-wiki-agent/1, at: 2026-11-18T02:35:40Z }
stale_after: 2027-02-17
sources:
  - id: pydantic-code-mode-benchmark
    resource: ../raw/why-code-mode-is-the-future/index.md
    scope: ../raw/why-code-mode-is-the-future/
    kind: article
    revision: sha256:4c4c5386d84ccbc9907ffeb4c539efe4f20c6b0bd46da20e5d6d2d2befb6681a
    title: "Code mode vs tool calling: a 5,276-run benchmark"
  - id: pydantic-code-sandboxes
    resource: ../raw/code-mode-vs-sandboxes/index.md
    scope: ../raw/code-mode-vs-sandboxes/
    kind: article
    revision: sha256:8d543df622eaaabd1fbf785550e6492c92479d39aefc1f1a94b9292057a6612b
    title: "Code mode vs sandboxes for AI agents"
---

**Code mode** lets a model write sandboxed Python that invokes registered tools, using loops, branches and concurrency to process intermediate data without returning every result to the model. A Pydantic vendor benchmark reports substantial gains on long, repetitive CRUD tasks, but overhead or correctness regressions on some small tasks and models. Results are **reported**, not independently reproduced.[^pydantic-code-mode-benchmark]

## How to use and contain it

For the benchmark's Pydantic AI `2.56.1.dev13` and Harness `0.56.1.dev13` at commit `b82f0f258f4d`, `CodeMode` exposes a `run_code` tool and wraps registered tools as async functions in Monty. `CodeMode(eager=True)` can begin executing a complete statement while the model is still writing the call. Selective tool sandboxing permits leaving other tools as direct calls. Speculation is distinct: tools must be declared safe for early execution; none in this benchmark were, so its speculative arm does not measure speculation's effect.[^pydantic-code-mode-benchmark]

The article reports that Monty starts without host filesystem, environment, clock or network access; tools and explicitly granted OS access are the escape routes. In the tested versions, defaults are 30 seconds of execution time and 256 MiB heap per snippet; the experiment additionally granted `OSAccess` with an in-memory filesystem and environment plus the host clock. These limits do not remove the authority of registered tools: validate and authorize their effects separately. A failed snippet retried after partial execution may repeat writes; three reported long-task failures created duplicate records.[^pydantic-code-mode-benchmark]

For debugging, the article reports that instrumented `run_code` and its tool calls have nested OpenTelemetry spans, but intermediate sandbox values can be harder to inspect. **Synthesis:** idempotent write operations and explicit retry policies are important safeguards; measure them on the application's own tools rather than treating the sandbox as transactional.[^pydantic-code-mode-benchmark]

## Code and workspace boundaries

**Reported, Pydantic AI and Harness version unspecified:** Code mode governs how the model orchestrates tools; a sandbox governs where code executes and what it can access. They can be used independently or combined. Monty restricts model-written code to exposed functions, but those functions run in the agent process and retain their own authority. `CodeMode(monty_sandbox_url=...)` can instead send the interpreter program to a remote Monty worker while tools stay local.[^pydantic-code-sandboxes]

The vendor's combined example uses `CodeMode()`, `FileSystem()`, `Shell()` and `ModalSandbox()`: file tools are callable within `run_code`, while `run_command` and `start_command` remain direct tools. File and shell operations target the workspace sandbox; the agent and model key stay in the application process. `CodeMode(mount=...)` mounts directories from the agent machine, not the remote workspace; use workspace file tools for files shared with remote commands. This is not a guarantee that exposed tools cannot disclose secrets or cause side effects.[^pydantic-code-sandboxes]

## Benchmark and interpretation

The vendor reports 5,276 graded runs across eight models, five small applications with paginated single-item CRUD tools, and three tiers: 50 everyday tasks, 12 long-horizon tasks, and five scaling tasks at 5–200 items. The arms used the same tools and settings except code mode; eager execution was enabled in the code-mode arm. Exact final state and required reply numbers were graded deterministically, with scripted passing and failing reference solutions. The 3,500 everyday runs include an additional speculative arm in the first batch; long and scaling had 576 and 1,200 runs respectively.[^pydantic-code-mode-benchmark]

| Reported outcome | Code mode versus direct calls |
| --- | --- |
| Long tasks, eight models | 58% lower cost, 51% lower wall time, +16.0 percentage points success; failures 67/288 versus 21/288. |
| Scaling at 200 items | Cost 47–75% lower and wall time 42–67% lower across five tasks; success 62–79% without versus 92–100% with code mode, 24 runs per arm per task. |
| Scaling at 5 items | Cost increased 21–38% on three of five tasks; by 50 items it was cheaper on four. |
| Everyday tasks | Overall cost fell 16% and success rose 1.6 points, described as noise; one model's success fell from 98% to 92%. |

These are task- and model-dependent vendor measurements, not a universal crossover threshold. At 200 items only five of 25 individual success gaps across all sizes cleared zero; the author notes small samples. Across long tasks input tokens fell 53% and output tokens 66%. Direct tool calling already batches independent calls—one response carried 200—so fewer model requests are not the main explanation: on the scaling tasks at 200 items, requests fell only 1–22% on average. The proposed mechanism is less tool-call text generated and less intermediate data repeatedly returned to the model; code mode also adds about 2,600 characters of guidance per request.[^pydantic-code-mode-benchmark]

Inventory grew more slowly in code mode but remained costly because all N input lines were in the prompt. Code that prints intermediate data back can also erase token savings; models can generate buggy snippets or make wrong state changes. A single-operation control group cost 8% more and took 16% longer with code mode; category subsets had too few tests for intervals.[^pydantic-code-mode-benchmark]

## Evidence and coverage limits

**Reported:** Michael Pfaffenberger's Pydantic article, published 2026-10-28, evaluates the publisher's own framework. The benchmark code is not public; its reported randomized blocks, bootstrap intervals, staged design, retries, price assumptions and two frozen ambiguous prompts cannot be independently audited from this capture. Provider defaults and pricing differ, and the deepseek server had shared, uncontrolled load; cross-tier wall-time comparisons for that model are unreliable. No package, benchmark, sandbox, code example or trace was run here. The article's external links were not fetched; license and capture date are unspecified.[^pydantic-code-mode-benchmark]

The local package contains `index.md` and ten SVGs. The hero is decorative; the other diagrams and charts are summarized by their text alternatives and surrounding article prose, so their image files were not separately inspected. No local supporting code or data was found. The closing installation block is promotional and omitted; its API shape is summarized above.

The 2026-11-10 Pydantic article by Marcelo Trylesinski is vendor-authored and specifies no Pydantic AI, Harness, or Monty version. Its three local SVG diagrams duplicate their alt text and surrounding prose and were not separately inspected; two embedded public traces and external links were not fetched. No example, remote worker, sandbox or trace was run; license and capture date are unspecified. Claims from it are **Reported**.[^pydantic-code-sandboxes]

## Relationships

- **Related:** [Pydantic AI CodeMode operations](pydantic-ai-code-mode-operations.md) details tool selection, execution limits, state and replay.

- **Uses:** [Pydantic AI workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md) to isolate tool-side file and command execution separately from model-written code.[^pydantic-code-sandboxes]

- **Uses:** [Pydantic AI Harness](pydantic-ai-harness.md) supplies the capability; the benchmark fixes the version and execution options.
- **Illustrates:** [Code as the agent graph](code-as-agent-graph.md): the model dynamically writes loops and fan-out rather than choosing a fixed workflow. This is a synthesis of the two pages.
- **Uses:** [Pydantic AI observability](pydantic-ai-observability.md) for traces of sandboxed tool calls, as reported for the tested configuration.[^pydantic-code-mode-benchmark]

[^pydantic-code-sandboxes]: [Code mode vs sandboxes for AI agents](../raw/code-mode-vs-sandboxes/index.md), “What code mode is”, “Where the sandbox boundary goes”, “Code mode and a workspace together”, and “Monty”.
[^pydantic-code-mode-benchmark]: [Code mode vs tool calling: a 5,276-run benchmark](../raw/why-code-mode-is-the-future/index.md), “The loop, and why it hurts”, “Code mode with guardrails”, “The benchmark”, “The longer the task, the bigger the gap”, “Models already batch”, “Where the tokens go”, “Everyday tasks”, “Where code mode costs”, “So why is it the future?”, and “What about speculation?”.
